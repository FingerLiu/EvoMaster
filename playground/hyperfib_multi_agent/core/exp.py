"""Auto Node Builder 多智能体实验实现

定义 Planning Agent -> Coding Agent -> Validation Agent 的三步协作工作流，
用于自动构建 hyper-fib 平台的工作流节点（Node）。
"""

import logging
from typing import Any
from evomaster.core.exp import BaseExp
from evomaster.agent import BaseAgent
from evomaster.utils.types import TaskInstance


class MultiAgentExp(BaseExp):
    """Auto Node Builder 多智能体实验类

    实现三步协作工作流，用于自动构建 hyper-fib 平台的工作流节点：
    1. Planning Agent 分析节点需求并制定开发计划
    2. Coding Agent 根据计划生成节点代码（node.py, node_manifest.json, node_test.py）
    3. Validation Agent 验证生成的节点代码是否正确、完整、符合 Schema 规范
    """

    def __init__(self, planning_agent, coding_agent, validation_agent, config):
        """初始化多智能体实验

        Args:
            planning_agent: Planning Agent 实例
            coding_agent: Coding Agent 实例
            validation_agent: Validation Agent 实例
            config: EvoMasterConfig 实例
        """
        # 为了兼容基类，传入第一个agent（planning_agent）
        # 但实际使用时会使用多个agent
        super().__init__(planning_agent, config)
        self.planning_agent = planning_agent
        self.coding_agent = coding_agent
        self.validation_agent = validation_agent
        self.logger = logging.getLogger(self.__class__.__name__)

    @property
    def exp_name(self) -> str:
        """返回实验阶段名称"""
        return "MultiAgent"

    def run(self, task_description: str, task_id: str = "exp_001") -> dict:
        """运行多智能体实验

        工作流：
        1. Planning Agent 分析节点需求并制定开发计划
        2. Coding Agent 根据计划生成节点代码
        3. Validation Agent 验证节点代码的正确性和完整性

        Args:
            task_description: 任务描述（包含节点的输入输出 Schema 等需求信息）
            task_id: 任务 ID

        Returns:
            执行结果字典
        """
        self.logger.info("Starting Auto Node Builder multi-agent task execution")
        self.logger.info(f"Task: {task_description}")

        results = {
            'task_description': task_description,
            'planning_result': None,
            'coding_result': None,
            'validation_result': None,
            'status': 'running',
        }

        # 设置当前exp信息，用于trajectory记录
        # exp_name 从类名自动推断（MultiAgentExp -> MultiAgent）
        BaseAgent.set_exp_info(exp_name=self.exp_name, exp_index=0)

        try:
            # Step 1: Planning Agent制定计划
            if self.planning_agent:
                self.logger.info("=" * 60)
                self.logger.info("Step 1: Planning Agent analyzing task...")
                self.logger.info("=" * 60)

                planning_task = TaskInstance(
                    task_id=f"{task_id}_planning",
                    task_type="planning",
                    description=task_description,
                    input_data={},
                )

                planning_trajectory = self.planning_agent.run(planning_task)
                results['planning_trajectory'] = planning_trajectory

                # 提取Planning Agent的回答
                planning_result = self._extract_agent_response(planning_trajectory)
                results['planning_result'] = planning_result

                self.logger.info("Planning completed")
                self.logger.info(f"Planning result: {planning_result[:200]}...")

            # Step 2: Coding Agent执行任务
            if self.coding_agent:
                self.logger.info("=" * 60)
                self.logger.info("Step 2: Coding Agent executing task...")
                self.logger.info("=" * 60)

                # 准备Coding Agent的用户提示词格式化参数
                # 使用prompt_format_kwargs来传递planning_result
                original_format_kwargs = self.coding_agent._prompt_format_kwargs.copy()
                self.coding_agent._prompt_format_kwargs.update({
                    'planning_result': results.get('planning_result', '')
                })

                # 创建任务实例
                coding_task = TaskInstance(
                    task_id=f"{task_id}_coding",
                    task_type="coding",
                    description=task_description,
                    input_data={},
                )

                coding_trajectory = self.coding_agent.run(coding_task)

                # 恢复原始格式化参数
                self.coding_agent._prompt_format_kwargs = original_format_kwargs

                # 提取Coding Agent的结果
                coding_result = self._extract_agent_response(coding_trajectory)
                results['coding_result'] = coding_result
                results['coding_trajectory'] = coding_trajectory

                self.logger.info("Coding completed")
                self.logger.info(f"Coding status: {coding_trajectory.status}")

            # Step 3: Validation Agent验证节点代码
            if self.validation_agent:
                self.logger.info("=" * 60)
                self.logger.info("Step 3: Validation Agent verifying node code...")
                self.logger.info("=" * 60)

                # 准备Validation Agent的用户提示词格式化参数
                # 传递planning_result和coding_result
                original_format_kwargs = self.validation_agent._prompt_format_kwargs.copy()
                self.validation_agent._prompt_format_kwargs.update({
                    'planning_result': results.get('planning_result', ''),
                    'coding_result': results.get('coding_result', ''),
                })

                # 创建任务实例
                validation_task = TaskInstance(
                    task_id=f"{task_id}_validation",
                    task_type="validation",
                    description=task_description,
                    input_data={},
                )

                validation_trajectory = self.validation_agent.run(validation_task)

                # 恢复原始格式化参数
                self.validation_agent._prompt_format_kwargs = original_format_kwargs

                # 提取Validation Agent的结果
                validation_result = self._extract_agent_response(validation_trajectory)
                results['validation_result'] = validation_result
                results['validation_trajectory'] = validation_trajectory

                self.logger.info("Validation completed")
                self.logger.info(f"Validation status: {validation_trajectory.status}")

            results['status'] = 'completed'
            self.logger.info("Auto Node Builder multi-agent task execution completed")

            # 保存结果到 self.results（用于 save_results）
            result = {
                "task_id": task_id,
                "status": results['status'],
                "steps": 0,  # 多agent场景下steps计算方式不同
                "planning_trajectory": results.get('planning_trajectory'),
                "coding_trajectory": results.get('coding_trajectory'),
                "validation_trajectory": results.get('validation_trajectory'),
                "planning_result": results.get('planning_result'),
                "coding_result": results.get('coding_result'),
                "validation_result": results.get('validation_result'),
            }
            self.results.append(result)

        except Exception as e:
            self.logger.error(f"Multi-agent task execution failed: {e}", exc_info=True)
            results['status'] = 'failed'
            results['error'] = str(e)

            # 保存失败结果
            result = {
                "task_id": task_id,
                "status": "failed",
                "steps": 0,
                "error": str(e),
            }
            self.results.append(result)

        return results


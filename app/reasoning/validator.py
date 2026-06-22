from app.reasoning.models import ExecutionPlan

class PlanValidationError(Exception):
    """Raised when an execution plan violates constraints."""
    pass

class PlanValidator:
    """Validates the structure and safety of an execution plan."""

    MAX_STEPS = 5

    @classmethod
    def validate(cls, plan: ExecutionPlan) -> None:
        """
        Validates the plan. Raises PlanValidationError if invalid.
        """
        if not plan.steps:
            raise PlanValidationError("Execution plan is empty.")
            
        if len(plan.steps) > cls.MAX_STEPS:
            raise PlanValidationError(f"Execution plan exceeds maximum allowed steps ({cls.MAX_STEPS}).")

        # Check for circular dependencies
        # Build adjacency list
        graph = {step.step_id: step.depends_on for step in plan.steps}
        
        # Ensure all dependencies point to valid steps
        valid_step_ids = set(graph.keys())
        for step_id, deps in graph.items():
            for dep in deps:
                if dep not in valid_step_ids:
                    raise PlanValidationError(f"Step {step_id} depends on non-existent step {dep}.")

        # Detect cycles using DFS
        visited = set()
        rec_stack = set()
        
        def is_cyclic(node):
            visited.add(node)
            rec_stack.add(node)
            for neighbor in graph.get(node, []):
                if neighbor not in visited:
                    if is_cyclic(neighbor):
                        return True
                elif neighbor in rec_stack:
                    return True
            rec_stack.remove(node)
            return False

        for node in valid_step_ids:
            if node not in visited:
                if is_cyclic(node):
                    raise PlanValidationError("Execution plan contains circular dependencies.")

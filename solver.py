"""Fixed three-round Inspect conversation with continuous history."""
from inspect_ai.model import ChatMessageUser
from inspect_ai.solver import solver, Solver, TaskState, Generate


@solver
def consensus_solver(turns: list[str]) -> Solver:
    async def solve(state: TaskState, generate: Generate) -> TaskState:
        for index in range(3):
            if index:
                state.messages.append(ChatMessageUser(content=turns[index]))
            state = await generate(state)
        return state
    return solve

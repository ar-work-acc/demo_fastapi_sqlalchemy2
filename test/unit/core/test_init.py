from core.initialize_data import start_async_session_to_run_async_function


async def test_stub():
    async def stub(*args, **kwargs):
        print("stub")
    await start_async_session_to_run_async_function(stub)

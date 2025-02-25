import marvin
import marvin.config
import pytest
import sqlmodel


@pytest.fixture(scope="session")
def session_tmp_path(tmp_path_factory):
    return tmp_path_factory.mktemp("marvin")


@pytest.fixture(scope="session", autouse=True)
async def test_database(session_tmp_path):
    """Set up the test database"""
    await marvin.infra.db.create_db()
    yield
    await marvin.infra.db.destroy_db(confirm=True)


@pytest.fixture(autouse=True)
async def clear_test_database(test_database, session):
    """Clear the test database"""
    yield

    for table in reversed(sqlmodel.SQLModel.metadata.sorted_tables):
        await session.execute(table.delete())

    await session.commit()


@pytest.fixture(autouse=True, scope="session")
async def temporary_chromadb(session_tmp_path):
    """Run chroma in a temporary directory"""
    marvin.settings.chroma = marvin.config.ChromaSettings(
        **marvin.settings.chroma.dict(exclude={"persist_directory"}),
        persist_directory=str(session_tmp_path / "chroma"),
    )


@pytest.fixture
async def session():
    async with marvin.infra.db.session_context() as session:
        yield session

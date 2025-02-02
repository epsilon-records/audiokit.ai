"""Tests for content generation functionality."""

import pytest
from unittest.mock import patch

from audiokitpro.marketing.generator import (
    EPKGenerator,
    InternalReportGenerator,
    BookingEmailGenerator,
    ContentGenerator,
)


@pytest.fixture
async def mock_content_generator(
    mock_artist_data, mock_knowledge_base, mock_openrouter_client
):
    """Create a mock content generator for testing."""
    with patch("audiokitpro.marketing.generator.KnowledgeBase") as mock_kb_class:
        mock_kb_class.return_value = mock_knowledge_base
        with patch(
            "audiokitpro.marketing.generator.OpenRouterClient"
        ) as mock_client_class:
            mock_client_class.return_value = mock_openrouter_client
            generator = ContentGenerator(
                artist_id=mock_artist_data.id, model_name="test-model"
            )
            yield generator


async def test_content_generator_initialization(mock_artist_data):
    """Test ContentGenerator initialization."""
    generator = ContentGenerator(artist_id=mock_artist_data.id, model_name="test-model")
    assert generator.artist_id == mock_artist_data.id
    assert generator.model_name == "test-model"


async def test_epk_generation(mock_content_generator):
    """Test EPK generation."""
    generator = EPKGenerator(
        artist_id=mock_content_generator.artist_id,
        model_name=mock_content_generator.model_name,
    )

    content = await generator.generate_epk()
    assert isinstance(content, str)
    assert len(content) > 0


async def test_report_generation(mock_content_generator):
    """Test internal report generation."""
    generator = InternalReportGenerator(
        artist_id=mock_content_generator.artist_id,
        model_name=mock_content_generator.model_name,
    )

    content = await generator.generate_report()
    assert isinstance(content, str)
    assert len(content) > 0


async def test_email_generation(mock_content_generator):
    """Test booking email generation."""
    generator = BookingEmailGenerator(
        artist_id=mock_content_generator.artist_id,
        model_name=mock_content_generator.model_name,
    )

    content = await generator.generate_email()
    assert isinstance(content, str)
    assert len(content) > 0


async def test_content_generation_error_handling(mock_content_generator):
    """Test error handling in content generation."""
    # Mock knowledge base query failure
    mock_content_generator.knowledge_base.query.side_effect = Exception("Query failed")

    with pytest.raises(Exception) as exc_info:
        await mock_content_generator.generate(
            task_description="Test task", query="Test query"
        )
    assert "Failed to generate content" in str(exc_info.value)


async def test_system_prompt_building(mock_content_generator):
    """Test system prompt building."""
    task = "Test task description"
    context = "Test context information"

    prompt = mock_content_generator._build_system_prompt(task, context)

    assert task in prompt
    assert context in prompt
    assert "Guidelines:" in prompt
    assert "Focus on accuracy" in prompt


async def test_content_generation_with_doc_types(mock_content_generator):
    """Test content generation with specific document types."""
    doc_types = ["artist_profile", "performances"]

    await mock_content_generator.generate(
        task_description="Test task", query="Test query", doc_types=doc_types
    )

    # Verify knowledge base was queried with correct doc_types
    mock_content_generator.knowledge_base.query.assert_called_once_with(
        query="Test query", doc_types=doc_types, top_k=5
    )

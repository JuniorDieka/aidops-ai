import asyncio
import json
from pathlib import Path

from app.api.dependencies import get_embedding_provider, get_retriever, get_vector_store
from app.config import settings
from app.core.models import FileType
from app.services.ingestion.chunker import DocumentChunker
from app.services.ingestion.pdf_parser import PDFParser


async def load_sample_data():
    print("Loading sample data...")

    embedding_provider = get_embedding_provider()
    vector_store = get_vector_store()
    chunker = DocumentChunker()

    sample_dir = Path(settings.sample_data_dir) / "pdfs"

    for txt_file in sample_dir.glob("*.txt"):
        print(f"Processing {txt_file.name}...")

        with open(txt_file, "r", encoding="utf-8") as f:
            content = f.read()

        pages = [{"page": 1, "content": content}]
        chunks = await chunker.chunk_documents(pages, txt_file.name)

        chunk_texts = [chunk.content for chunk in chunks]
        embeddings = await embedding_provider.embed_batch(chunk_texts)

        for chunk, embedding in zip(chunks, embeddings):
            chunk.embedding = embedding

        await vector_store.add_chunks(chunks)

    print(f"Loaded {await vector_store.count()} chunks into vector store")


async def run_evaluation():
    print("\n" + "=" * 80)
    print("AidOps AI - RAG Evaluation Harness")
    print("=" * 80 + "\n")

    await load_sample_data()

    test_cases_path = Path(__file__).parent / "test_cases.json"
    with open(test_cases_path, "r") as f:
        test_cases = json.load(f)

    retriever = get_retriever()

    results = {
        "total_cases": len(test_cases),
        "passed": 0,
        "failed": 0,
        "cases": [],
    }

    for test_case in test_cases:
        print(f"\nTest Case {test_case['id']}: {test_case['category']}")
        print(f"Query: {test_case['query']}")

        try:
            chunks, citations = await retriever.retrieve(test_case["query"])

            retrieved_sources = [c.source_file for c in citations]
            retrieved_content = " ".join([chunk.content for chunk in chunks])

            faithfulness_score = sum(
                1 for term in test_case["expected_answer_contains"] if term.lower() in retrieved_content.lower()
            ) / len(test_case["expected_answer_contains"])

            source_hit = any(
                expected_source in source for expected_source in test_case["expected_sources"] for source in retrieved_sources
            )

            citation_score = len(citations) / 5.0 if len(citations) <= 5 else 1.0

            avg_relevance = sum(c.score for c in citations) / len(citations) if citations else 0

            passed = faithfulness_score >= 0.5 and source_hit

            case_result = {
                "id": test_case["id"],
                "query": test_case["query"],
                "passed": passed,
                "faithfulness_score": round(faithfulness_score, 2),
                "source_hit": source_hit,
                "citation_count": len(citations),
                "avg_relevance_score": round(avg_relevance, 2),
                "retrieved_sources": retrieved_sources,
            }

            results["cases"].append(case_result)

            if passed:
                results["passed"] += 1
                print("✓ PASSED")
            else:
                results["failed"] += 1
                print("✗ FAILED")

            print(f"  Faithfulness: {faithfulness_score:.2f}")
            print(f"  Source Hit: {source_hit}")
            print(f"  Citations: {len(citations)}")
            print(f"  Avg Relevance: {avg_relevance:.2f}")

        except Exception as e:
            print(f"✗ ERROR: {str(e)}")
            results["failed"] += 1
            results["cases"].append(
                {
                    "id": test_case["id"],
                    "query": test_case["query"],
                    "passed": False,
                    "error": str(e),
                }
            )

    print("\n" + "=" * 80)
    print("EVALUATION SUMMARY")
    print("=" * 80)
    print(f"Total Test Cases: {results['total_cases']}")
    print(f"Passed: {results['passed']}")
    print(f"Failed: {results['failed']}")
    print(f"Success Rate: {results['passed'] / results['total_cases'] * 100:.1f}%")
    print("=" * 80 + "\n")

    results_dir = Path(__file__).parent / "results"
    results_dir.mkdir(exist_ok=True)

    results_file = results_dir / "evaluation_results.json"
    with open(results_file, "w") as f:
        json.dump(results, f, indent=2)

    print(f"Results saved to: {results_file}")

    return results


if __name__ == "__main__":
    asyncio.run(run_evaluation())

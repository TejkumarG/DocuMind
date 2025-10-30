#!/usr/bin/env python3
"""
Test script for DSPy RAG API

Tests the API with the question: "What did WESTDALE do in June 2022?"
"""

import httpx
import json
import sys


def test_health_check(base_url: str = "http://localhost:8001"):
    """Test the health check endpoint"""
    print("=" * 60)
    print("Testing Health Check...")
    print("=" * 60)

    try:
        response = httpx.get(f"{base_url}/api/v1/health", timeout=10.0)
        response.raise_for_status()
        result = response.json()
        print("✓ Health check passed!")
        print(f"  Status: {result.get('status')}")
        print(f"  Service: {result.get('service')}")
        return True
    except Exception as e:
        print(f"✗ Health check failed: {e}")
        return False


def test_ask_question(base_url: str = "http://localhost:8001"):
    """Test asking a question to the RAG API"""
    print("\n" + "=" * 60)
    print("Testing Question Answering...")
    print("=" * 60)

    question = "What did WESTDALE do in June 2022?"
    print(f"\nQuestion: {question}\n")

    try:
        response = httpx.post(
            f"{base_url}/api/v1/ask",
            json={"question": question},
            timeout=60.0
        )
        response.raise_for_status()
        result = response.json()

        print("✓ Question answered successfully!\n")
        print(f"Question: {result.get('question')}")
        print(f"\nAnswer:\n{result.get('answer')}\n")
        print(f"Context chunks used: {len(result.get('context_used', []))}")

        # Print first context chunk (truncated)
        if result.get('context_used'):
            first_context = result['context_used'][0]
            print(f"\nFirst context chunk (truncated):")
            print(f"{first_context[:200]}...\n")

        return True
    except httpx.HTTPStatusError as e:
        print(f"✗ HTTP Error: {e.response.status_code}")
        print(f"  Response: {e.response.text}")
        return False
    except Exception as e:
        print(f"✗ Request failed: {e}")
        return False


def test_retrieval_api():
    """Test the retrieval API directly"""
    print("\n" + "=" * 60)
    print("Testing Retrieval API (localhost:8000)...")
    print("=" * 60)

    try:
        response = httpx.post(
            "http://localhost:8000/retrieve",
            json={
                "query": "What did WESTDALE do in June 2022?",
                "min_chunks": 3,
                "max_chunks": 6
            },
            timeout=30.0
        )
        response.raise_for_status()
        result = response.json()

        print("✓ Retrieval API is working!")
        print(f"  Total results: {result.get('total_results')}")
        print(f"  Chunks returned: {len(result.get('chunks', []))}")
        return True
    except Exception as e:
        print(f"✗ Retrieval API failed: {e}")
        print("  Make sure the retrieval API is running on localhost:8000")
        return False


def main():
    """Run all tests"""
    print("\n")
    print("╔" + "=" * 58 + "╗")
    print("║" + " " * 58 + "║")
    print("║" + "  DSPy RAG API - Test Suite".center(58) + "║")
    print("║" + " " * 58 + "║")
    print("╚" + "=" * 58 + "╝")
    print("\n")

    # Test retrieval API first
    retrieval_ok = test_retrieval_api()

    if not retrieval_ok:
        print("\n⚠️  Warning: Retrieval API is not available.")
        print("   The RAG API will not work without it.")

    # Test health check
    health_ok = test_health_check()

    if not health_ok:
        print("\n✗ DSPy RAG API is not running!")
        print("  Start it with: docker-compose up")
        print("  Or: python app.py")
        sys.exit(1)

    # Test question answering
    ask_ok = test_ask_question()

    # Summary
    print("\n" + "=" * 60)
    print("Test Summary")
    print("=" * 60)
    print(f"Retrieval API:  {'✓ PASS' if retrieval_ok else '✗ FAIL'}")
    print(f"Health Check:   {'✓ PASS' if health_ok else '✗ FAIL'}")
    print(f"Ask Question:   {'✓ PASS' if ask_ok else '✗ FAIL'}")
    print("=" * 60)

    if retrieval_ok and health_ok and ask_ok:
        print("\n🎉 All tests passed!")
        sys.exit(0)
    else:
        print("\n⚠️  Some tests failed.")
        sys.exit(1)


if __name__ == "__main__":
    main()

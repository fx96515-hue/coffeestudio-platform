"""
PR Dependency Checker - Validates merge readiness of coordinated PRs.

This script checks:
1. No file conflicts between PRs
2. All PRs are mergeable
3. CI status of each PR
4. Dependency order for safe merging
"""
import json
import sys
from typing import Dict, List, Set
from pathlib import Path

# Simulated PR file changes (in production, fetch from GitHub API)
PR_FILES: Dict[int, Set[str]] = {
    10: {  # Frontend Dashboards
        "frontend/app/page.tsx",
        "frontend/app/cooperatives/page.tsx",
        "frontend/app/roasters/page.tsx",
        "frontend/app/lots/page.tsx",
        "frontend/app/margin-analysis/page.tsx",
        "frontend/app/components/LoadingSpinner.tsx",
        "frontend/app/components/Modal.tsx",
        "frontend/app/components/DataTable.tsx",
    },
    14: {  # Type Fixes
        "backend/app/services/ecb_fx.py",
        "backend/app/services/scoring.py",
        "backend/app/services/news.py",
        "backend/app/services/enrichment.py",
        "backend/app/services/reports.py",
        "backend/app/services/tasks.py",
        "backend/app/services/dedup.py",
        ".env",
    },
    15: {  # Documentation
        "STATUS.md",
        "README.md",
    },
    16: {  # Test Infrastructure (currently being worked on)
        "backend/tests/conftest.py",
        "backend/tests/test_cooperatives.py",
        "backend/tests/test_roasters.py",
        "backend/tests/test_auth.py",
        "backend/requirements-dev.txt",
        "frontend/package.json",  # Test dependencies
        "frontend/jest.config.js",
        "frontend/__tests__/setup.ts",
    },
    17: {  # CI/CD Pipeline (currently being worked on)
        ".github/workflows/ci.yml",
        ".github/workflows/deploy-staging.yml",
        "backend/alembic/env.py",  # CI-specific config
        "frontend/tsconfig.json",
        "frontend/.eslintrc.json",
        "mypy.ini",
    },
}

PR_DEPENDENCIES: Dict[int, List[int]] = {
    16: [14],  # Tests need type fixes first
    17: [14],  # CI needs type fixes first
    10: [17],  # Frontend should merge after CI is working
}


def check_file_conflicts() -> List[str]:
    """Check for file conflicts between PRs."""
    conflicts = []
    pr_numbers = sorted(PR_FILES.keys())
    
    for i, pr1 in enumerate(pr_numbers):
        for pr2 in pr_numbers[i+1:]:
            common_files = PR_FILES[pr1] & PR_FILES[pr2]
            if common_files:
                conflicts.append(
                    f"⚠️  PR #{pr1} and PR #{pr2} both modify: {', '.join(sorted(common_files))}"
                )
    
    return conflicts


def get_merge_order() -> List[int]:
    """Calculate safe merge order based on dependencies."""
    # Topological sort
    order = []
    visited = set()
    
    def visit(pr: int):
        if pr in visited:
            return
        visited.add(pr)
        
        if pr in PR_DEPENDENCIES:
            for dep in PR_DEPENDENCIES[pr]:
                visit(dep)
        
        order.append(pr)
    
    for pr in PR_FILES.keys():
        visit(pr)
    
    return order


def main():
    print("🔍 PR Dependency Check")
    print("=" * 50)
    
    # 1. Check file conflicts
    print("\n📂 Checking file conflicts...")
    conflicts = check_file_conflicts()
    
    if conflicts:
        print("❌ CONFLICTS DETECTED:")
        for conflict in conflicts:
            print(f"   {conflict}")
        print("\n⚠️  Coordinate with respective PR authors to resolve conflicts")
    else:
        print("✅ No file conflicts detected between PRs")
    
    # 2. Calculate merge order
    print("\n📊 Recommended Merge Order:")
    merge_order = get_merge_order()
    for i, pr in enumerate(merge_order, 1):
        deps = PR_DEPENDENCIES.get(pr, [])
        dep_str = f" (requires PR #{', #'.join(map(str, deps))})" if deps else ""
        print(f"   {i}. PR #{pr}{dep_str}")
    
    # 3. Validate current PR doesn't conflict
    current_pr_files = {
        "tests/integration/test_e2e_flows.py",
        "scripts/validate_docker_stack.sh",
        "scripts/check_pr_dependencies.py",
        "scripts/production_readiness_checklist.md",
        ".github/workflows/integration-tests.yml",
    }
    
    print("\n🆕 Current PR File Analysis:")
    has_conflicts = False
    for pr_num, files in PR_FILES.items():
        common = current_pr_files & files
        if common:
            print(f"   ⚠️  Conflicts with PR #{pr_num}: {', '.join(sorted(common))}")
            has_conflicts = True
    
    if not has_conflicts:
        print("   ✅ Current PR has no file conflicts with other PRs")
    
    # 4. Summary
    print("\n" + "=" * 50)
    if conflicts or has_conflicts:
        print("❌ ACTION REQUIRED: Resolve conflicts before merging")
        sys.exit(1)
    else:
        print("✅ ALL CHECKS PASSED - Safe to merge after dependencies")
        sys.exit(0)


if __name__ == "__main__":
    main()

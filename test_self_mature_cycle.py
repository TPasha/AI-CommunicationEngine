"""
Self-Mature Cycle Testing Script
Runs comprehensive tests across multiple cycles to validate all components
"""

import asyncio
import sys
from typing import List, Dict, Any
from datetime import datetime
import traceback

# Test Cases Configuration
TEST_CASES = {
    "imports": [
        "fastapi",
        "uvicorn",
        "pydantic",
        "sqlalchemy",
        "openai",
        "transformers",
        "torch",
        "requests",
        "twilio",
        "vonage",
        "firebase_admin",
        "loguru",
        "numpy",
        "librosa",
        "pytest",
        "redis"
    ],
    "async_operations": [
        "async_file_operations",
        "concurrent_tasks",
        "event_loop_handling"
    ],
    "api_endpoints": [
        "health_check",
        "voice_processing",
        "communication_channels",
        "authentication"
    ],
    "data_validation": [
        "pydantic_models",
        "request_validation",
        "response_serialization"
    ]
}

class SelfMatureCycleTester:
    def __init__(self, cycles: int = 3):
        self.cycles = cycles
        self.results = []
        self.start_time = None
        self.end_time = None
        
    def log(self, message: str, level: str = "INFO"):
        """Log messages with timestamp"""
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        print(f"[{timestamp}] [{level}] {message}")
    
    def test_imports(self) -> Dict[str, Any]:
        """Test if all required packages can be imported"""
        self.log("Testing package imports...")
        results = {"passed": [], "failed": []}
        
        for package in TEST_CASES["imports"]:
            try:
                __import__(package)
                results["passed"].append(package)
                self.log(f"✓ {package} imported successfully", "SUCCESS")
            except ImportError as e:
                results["failed"].append({"package": package, "error": str(e)})
                self.log(f"✗ {package} import failed: {e}", "ERROR")
        
        return results
    
    async def test_async_operations(self) -> Dict[str, Any]:
        """Test async functionality"""
        self.log("Testing async operations...")
        results = {"passed": [], "failed": []}
        
        # Test 1: Basic async function
        try:
            async def sample_async_task():
                await asyncio.sleep(0.1)
                return "success"
            
            result = await sample_async_task()
            results["passed"].append("basic_async_function")
            self.log("✓ Basic async function works", "SUCCESS")
        except Exception as e:
            results["failed"].append({"test": "basic_async_function", "error": str(e)})
            self.log(f"✗ Basic async function failed: {e}", "ERROR")
        
        # Test 2: Concurrent tasks
        try:
            async def concurrent_task(n):
                await asyncio.sleep(0.05)
                return n * 2
            
            tasks = [concurrent_task(i) for i in range(5)]
            concurrent_results = await asyncio.gather(*tasks)
            results["passed"].append("concurrent_tasks")
            self.log(f"✓ Concurrent tasks completed: {concurrent_results}", "SUCCESS")
        except Exception as e:
            results["failed"].append({"test": "concurrent_tasks", "error": str(e)})
            self.log(f"✗ Concurrent tasks failed: {e}", "ERROR")
        
        return results
    
    def test_pydantic_models(self) -> Dict[str, Any]:
        """Test Pydantic validation"""
        self.log("Testing Pydantic models...")
        results = {"passed": [], "failed": []}
        
        try:
            from pydantic import BaseModel, field_validator
            
            class TestModel(BaseModel):
                name: str
                age: int
                email: str
            
            # Valid model
            valid_model = TestModel(name="Test", age=25, email="test@example.com")
            results["passed"].append("valid_model_creation")
            self.log("✓ Valid Pydantic model created", "SUCCESS")
            
            # Test validation
            try:
                invalid_model = TestModel(name="Test", age="invalid", email="test@example.com")
                results["failed"].append({"test": "invalid_model_validation", "error": "Should have failed"})
            except Exception:
                results["passed"].append("model_validation")
                self.log("✓ Pydantic validation working correctly", "SUCCESS")
                
        except Exception as e:
            results["failed"].append({"test": "pydantic_models", "error": str(e)})
            self.log(f"✗ Pydantic test failed: {e}", "ERROR")
        
        return results
    
    def test_fastapi_components(self) -> Dict[str, Any]:
        """Test FastAPI components"""
        self.log("Testing FastAPI components...")
        results = {"passed": [], "failed": []}
        
        try:
            from fastapi import FastAPI, HTTPException
            from pydantic import BaseModel
            
            app = FastAPI()
            
            class Item(BaseModel):
                name: str
                price: float
            
            @app.get("/health")
            def health_check():
                return {"status": "healthy"}
            
            @app.post("/items/")
            def create_item(item: Item):
                return item
            
            results["passed"].append("fastapi_app_creation")
            self.log("✓ FastAPI app created successfully", "SUCCESS")
            
        except Exception as e:
            results["failed"].append({"test": "fastapi_components", "error": str(e)})
            self.log(f"✗ FastAPI test failed: {e}", "ERROR")
        
        return results
    
    def test_database_components(self) -> Dict[str, Any]:
        """Test SQLAlchemy components"""
        self.log("Testing database components...")
        results = {"passed": [], "failed": []}
        
        try:
            from sqlalchemy import create_engine, Column, Integer, String
            from sqlalchemy.ext.declarative import declarative_base
            from sqlalchemy.orm import sessionmaker
            
            Base = declarative_base()
            
            class User(Base):
                __tablename__ = 'test_users'
                id = Column(Integer, primary_key=True)
                name = Column(String(50))
            
            results["passed"].append("sqlalchemy_model_creation")
            self.log("✓ SQLAlchemy models created", "SUCCESS")
            
        except Exception as e:
            results["failed"].append({"test": "database_components", "error": str(e)})
            self.log(f"✗ Database test failed: {e}", "ERROR")
        
        return results
    
    def test_ai_ml_components(self) -> Dict[str, Any]:
        """Test AI/ML library components"""
        self.log("Testing AI/ML components...")
        results = {"passed": [], "failed": []}
        
        try:
            import numpy as np
            arr = np.array([1, 2, 3, 4, 5])
            results["passed"].append("numpy_operations")
            self.log(f"✓ NumPy operations work: mean={arr.mean()}", "SUCCESS")
        except Exception as e:
            results["failed"].append({"test": "numpy_operations", "error": str(e)})
            self.log(f"✗ NumPy test failed: {e}", "ERROR")
        
        try:
            import torch
            tensor = torch.tensor([1.0, 2.0, 3.0])
            results["passed"].append("torch_tensor_creation")
            self.log(f"✓ PyTorch tensor created: {tensor.shape}", "SUCCESS")
        except Exception as e:
            results["failed"].append({"test": "torch_tensor_creation", "error": str(e)})
            self.log(f"✗ PyTorch test failed: {e}", "ERROR")
        
        return results
    
    def test_communication_apis(self) -> Dict[str, Any]:
        """Test communication API libraries"""
        self.log("Testing communication APIs...")
        results = {"passed": [], "failed": []}
        
        try:
            import twilio
            from twilio.rest import Client
            results["passed"].append("twilio_import")
            self.log("✓ Twilio library available", "SUCCESS")
        except Exception as e:
            results["failed"].append({"test": "twilio_import", "error": str(e)})
            self.log(f"✗ Twilio test failed: {e}", "ERROR")
        
        try:
            import vonage
            results["passed"].append("vonage_import")
            self.log("✓ Vonage library available", "SUCCESS")
        except Exception as e:
            results["failed"].append({"test": "vonage_import", "error": str(e)})
            self.log(f"✗ Vonage test failed: {e}", "ERROR")
        
        return results
    
    async def run_cycle(self, cycle_number: int) -> Dict[str, Any]:
        """Run a complete test cycle"""
        self.log(f"{'='*60}", "INFO")
        self.log(f"STARTING CYCLE {cycle_number}", "INFO")
        self.log(f"{'='*60}", "INFO")
        
        cycle_results = {
            "cycle": cycle_number,
            "timestamp": datetime.now().isoformat(),
            "tests": {}
        }
        
        # Run all test suites
        cycle_results["tests"]["imports"] = self.test_imports()
        cycle_results["tests"]["async_operations"] = await self.test_async_operations()
        cycle_results["tests"]["pydantic_models"] = self.test_pydantic_models()
        cycle_results["tests"]["fastapi_components"] = self.test_fastapi_components()
        cycle_results["tests"]["database_components"] = self.test_database_components()
        cycle_results["tests"]["ai_ml_components"] = self.test_ai_ml_components()
        cycle_results["tests"]["communication_apis"] = self.test_communication_apis()
        
        # Calculate cycle summary
        total_passed = sum(len(test["passed"]) for test in cycle_results["tests"].values())
        total_failed = sum(len(test["failed"]) for test in cycle_results["tests"].values())
        
        cycle_results["summary"] = {
            "total_passed": total_passed,
            "total_failed": total_failed,
            "success_rate": f"{(total_passed / (total_passed + total_failed) * 100):.2f}%" if (total_passed + total_failed) > 0 else "N/A"
        }
        
        self.log(f"Cycle {cycle_number} Summary: {total_passed} passed, {total_failed} failed", "INFO")
        self.log(f"{'='*60}\n", "INFO")
        
        return cycle_results
    
    async def run_all_cycles(self):
        """Run all test cycles"""
        self.start_time = datetime.now()
        self.log(f"Starting Self-Mature Cycle Testing - {self.cycles} cycles", "INFO")
        
        for cycle in range(1, self.cycles + 1):
            try:
                cycle_result = await self.run_cycle(cycle)
                self.results.append(cycle_result)
                
                # Wait between cycles (except last one)
                if cycle < self.cycles:
                    self.log(f"Waiting before next cycle...\n", "INFO")
                    await asyncio.sleep(2)
                    
            except Exception as e:
                self.log(f"Critical error in cycle {cycle}: {e}", "ERROR")
                self.log(traceback.format_exc(), "ERROR")
        
        self.end_time = datetime.now()
        self.print_final_report()
    
    def print_final_report(self):
        """Print final comprehensive report"""
        self.log(f"\n{'#'*60}", "INFO")
        self.log("FINAL SELF-MATURE CYCLE REPORT", "INFO")
        self.log(f"{'#'*60}", "INFO")
        
        duration = (self.end_time - self.start_time).total_seconds()
        self.log(f"Total Duration: {duration:.2f} seconds", "INFO")
        self.log(f"Total Cycles: {len(self.results)}", "INFO")
        
        # Aggregate results
        all_passed = []
        all_failed = []
        
        for result in self.results:
            for test_name, test_result in result["tests"].items():
                all_passed.extend(test_result["passed"])
                all_failed.extend(test_result["failed"])
        
        self.log(f"\nOverall Statistics:", "INFO")
        self.log(f"  Total Tests Passed: {len(all_passed)}", "SUCCESS")
        self.log(f"  Total Tests Failed: {len(all_failed)}", "ERROR" if all_failed else "INFO")
        
        if all_failed:
            self.log(f"\nFailed Tests Details:", "ERROR")
            seen_failures = set()
            for failed in all_failed:
                if isinstance(failed, dict):
                    key = failed.get('test', failed.get('package', 'unknown'))
                    if key not in seen_failures:
                        seen_failures.add(key)
                        self.log(f"  - {key}: {failed.get('error', 'No error message')}", "ERROR")
        
        success_rate = (len(all_passed) / (len(all_passed) + len(all_failed)) * 100) if (len(all_passed) + len(all_failed)) > 0 else 0
        self.log(f"\nOverall Success Rate: {success_rate:.2f}%", "SUCCESS" if success_rate > 90 else "WARNING")
        
        # Component breakdown
        self.log(f"\nComponent Test Summary:", "INFO")
        for result in self.results:
            if result["cycle"] == 1:  # Just show first cycle breakdown
                for test_name, test_result in result["tests"].items():
                    passed = len(test_result["passed"])
                    failed = len(test_result["failed"])
                    self.log(f"  {test_name}: {passed} passed, {failed} failed", "INFO")
        
        self.log(f"\n{'#'*60}\n", "INFO")

async def main():
    """Main entry point"""
    print("\n" + "="*60)
    print("AI COMMUNICATION ENGINE - SELF-MATURE CYCLE TESTER")
    print("="*60 + "\n")
    
    # Configure number of cycles
    cycles = 3
    
    tester = SelfMatureCycleTester(cycles=cycles)
    await tester.run_all_cycles()
    
    # Exit with appropriate code
    total_failed = sum(
        len(result["tests"][test]["failed"]) 
        for result in tester.results 
        for test in result["tests"]
    )
    
    print(f"\nTest Summary: {'ALL TESTS PASSED' if total_failed == 0 else f'{total_failed} TESTS FAILED'}")
    sys.exit(0 if total_failed == 0 else 1)

if __name__ == "__main__":
    asyncio.run(main())

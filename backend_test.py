#!/usr/bin/env python3
"""
Comprehensive Backend API Testing for Testnet Mentoring Platform
Tests all backend functionality including authentication, search, chat, profiles, and admin features.
"""

import requests
import json
import time
import asyncio
import socketio
from datetime import datetime
import sys
import os

# Backend URL from frontend .env
BACKEND_URL = "https://61353841-f231-419a-bf73-a38fd7bf441c.preview.emergentagent.com/api"

class TestnetAPITester:
    def __init__(self):
        self.base_url = BACKEND_URL
        self.session = requests.Session()
        self.tokens = {}
        self.users = {}
        self.profiles = {}
        self.conversations = {}
        self.test_results = {
            "User Authentication System": {"passed": 0, "failed": 0, "errors": []},
            "Mentor Search API": {"passed": 0, "failed": 0, "errors": []},
            "Real-time Chat System": {"passed": 0, "failed": 0, "errors": []},
            "Profile Management": {"passed": 0, "failed": 0, "errors": []},
            "Admin Dashboard API": {"passed": 0, "failed": 0, "errors": []}
        }
        
    def log_result(self, test_category, test_name, success, error_msg=None):
        """Log test results"""
        if success:
            self.test_results[test_category]["passed"] += 1
            print(f"✅ {test_name}")
        else:
            self.test_results[test_category]["failed"] += 1
            self.test_results[test_category]["errors"].append(f"{test_name}: {error_msg}")
            print(f"❌ {test_name}: {error_msg}")
    
    def test_user_authentication(self):
        """Test User Authentication System"""
        print("\n🔐 Testing User Authentication System...")
        
        # Test 1: Register new seeker
        try:
            seeker_data = {
                "email": "sarah.johnson@email.com",
                "name": "Sarah Johnson",
                "password": "SecurePass123!",
                "role": "seeker"
            }
            response = self.session.post(f"{self.base_url}/auth/register", json=seeker_data)
            
            if response.status_code == 200:
                token_data = response.json()
                self.tokens["seeker"] = token_data["access_token"]
                self.users["seeker"] = seeker_data
                self.log_result("User Authentication System", "Seeker Registration", True)
            else:
                self.log_result("User Authentication System", "Seeker Registration", False, f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("User Authentication System", "Seeker Registration", False, str(e))
        
        # Test 2: Register new mentor
        try:
            mentor_data = {
                "email": "alex.mentor@email.com",
                "name": "Alex Rodriguez",
                "password": "MentorPass456!",
                "role": "mentor"
            }
            response = self.session.post(f"{self.base_url}/auth/register", json=mentor_data)
            
            if response.status_code == 200:
                token_data = response.json()
                self.tokens["mentor"] = token_data["access_token"]
                self.users["mentor"] = mentor_data
                self.log_result("User Authentication System", "Mentor Registration", True)
            else:
                self.log_result("User Authentication System", "Mentor Registration", False, f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("User Authentication System", "Mentor Registration", False, str(e))
        
        # Test 3: Register admin user
        try:
            admin_data = {
                "email": "admin@testnet.com",
                "name": "Admin User",
                "password": "AdminPass789!",
                "role": "admin"
            }
            response = self.session.post(f"{self.base_url}/auth/register", json=admin_data)
            
            if response.status_code == 200:
                token_data = response.json()
                self.tokens["admin"] = token_data["access_token"]
                self.users["admin"] = admin_data
                self.log_result("User Authentication System", "Admin Registration", True)
            else:
                self.log_result("User Authentication System", "Admin Registration", False, f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("User Authentication System", "Admin Registration", False, str(e))
        
        # Test 4: Login with seeker credentials
        try:
            login_data = {
                "email": "sarah.johnson@email.com",
                "password": "SecurePass123!"
            }
            response = self.session.post(f"{self.base_url}/auth/login", json=login_data)
            
            if response.status_code == 200:
                self.log_result("User Authentication System", "Seeker Login", True)
            else:
                self.log_result("User Authentication System", "Seeker Login", False, f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("User Authentication System", "Seeker Login", False, str(e))
        
        # Test 5: Test JWT token validation
        try:
            headers = {"Authorization": f"Bearer {self.tokens.get('seeker', '')}"}
            response = self.session.get(f"{self.base_url}/users/me", headers=headers)
            
            if response.status_code == 200:
                user_data = response.json()
                if user_data.get("email") == "sarah.johnson@email.com":
                    self.log_result("User Authentication System", "JWT Token Validation", True)
                else:
                    self.log_result("User Authentication System", "JWT Token Validation", False, "User data mismatch")
            else:
                self.log_result("User Authentication System", "JWT Token Validation", False, f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("User Authentication System", "JWT Token Validation", False, str(e))
        
        # Test 6: Test invalid credentials
        try:
            invalid_login = {
                "email": "sarah.johnson@email.com",
                "password": "WrongPassword"
            }
            response = self.session.post(f"{self.base_url}/auth/login", json=invalid_login)
            
            if response.status_code == 401:
                self.log_result("User Authentication System", "Invalid Credentials Rejection", True)
            else:
                self.log_result("User Authentication System", "Invalid Credentials Rejection", False, f"Expected 401, got {response.status_code}")
        except Exception as e:
            self.log_result("User Authentication System", "Invalid Credentials Rejection", False, str(e))
    
    def test_profile_management(self):
        """Test Profile Management"""
        print("\n👤 Testing Profile Management...")
        
        # Test 1: Get initial profile (should be empty)
        try:
            headers = {"Authorization": f"Bearer {self.tokens.get('mentor', '')}"}
            response = self.session.get(f"{self.base_url}/users/me/profile", headers=headers)
            
            if response.status_code == 200:
                self.log_result("Profile Management", "Get Initial Profile", True)
            else:
                self.log_result("Profile Management", "Get Initial Profile", False, f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("Profile Management", "Get Initial Profile", False, str(e))
        
        # Test 2: Update mentor profile
        try:
            profile_data = {
                "bio": "Experienced software engineer with 8+ years in full-stack development. Passionate about mentoring junior developers and sharing knowledge in React, Python, and cloud technologies.",
                "skills": ["Python", "React", "Node.js", "AWS", "Docker", "MongoDB"],
                "experience_years": 8,
                "hourly_rate": 75.0,
                "available": True,
                "avatar_url": "https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=150"
            }
            headers = {"Authorization": f"Bearer {self.tokens.get('mentor', '')}"}
            response = self.session.put(f"{self.base_url}/users/me/profile", json=profile_data, headers=headers)
            
            if response.status_code == 200:
                updated_profile = response.json()
                self.profiles["mentor"] = updated_profile
                self.log_result("Profile Management", "Update Mentor Profile", True)
            else:
                self.log_result("Profile Management", "Update Mentor Profile", False, f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("Profile Management", "Update Mentor Profile", False, str(e))
        
        # Test 3: Update seeker profile
        try:
            seeker_profile_data = {
                "bio": "Computer science student looking to learn web development and gain industry insights. Interested in frontend technologies and user experience design.",
                "skills": ["HTML", "CSS", "JavaScript", "Learning React"],
                "experience_years": 1,
                "hourly_rate": 0.0,
                "available": True,
                "avatar_url": "https://images.unsplash.com/photo-1494790108755-2616b612b786?w=150"
            }
            headers = {"Authorization": f"Bearer {self.tokens.get('seeker', '')}"}
            response = self.session.put(f"{self.base_url}/users/me/profile", json=seeker_profile_data, headers=headers)
            
            if response.status_code == 200:
                self.profiles["seeker"] = response.json()
                self.log_result("Profile Management", "Update Seeker Profile", True)
            else:
                self.log_result("Profile Management", "Update Seeker Profile", False, f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("Profile Management", "Update Seeker Profile", False, str(e))
        
        # Test 4: Verify profile data persistence
        try:
            headers = {"Authorization": f"Bearer {self.tokens.get('mentor', '')}"}
            response = self.session.get(f"{self.base_url}/users/me/profile", headers=headers)
            
            if response.status_code == 200:
                profile = response.json()
                if profile.get("experience_years") == 8 and "Python" in profile.get("skills", []):
                    self.log_result("Profile Management", "Profile Data Persistence", True)
                else:
                    self.log_result("Profile Management", "Profile Data Persistence", False, "Profile data not persisted correctly")
            else:
                self.log_result("Profile Management", "Profile Data Persistence", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Profile Management", "Profile Data Persistence", False, str(e))
    
    def test_admin_dashboard(self):
        """Test Admin Dashboard API"""
        print("\n🛡️ Testing Admin Dashboard API...")
        
        # Test 1: Get mentors list as admin
        try:
            headers = {"Authorization": f"Bearer {self.tokens.get('admin', '')}"}
            response = self.session.get(f"{self.base_url}/admin/mentors", headers=headers)
            
            if response.status_code == 200:
                mentors = response.json()
                self.log_result("Admin Dashboard API", "Get Mentors List", True)
            else:
                self.log_result("Admin Dashboard API", "Get Mentors List", False, f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("Admin Dashboard API", "Get Mentors List", False, str(e))
        
        # Test 2: Try to access admin endpoint as non-admin (should fail)
        try:
            headers = {"Authorization": f"Bearer {self.tokens.get('seeker', '')}"}
            response = self.session.get(f"{self.base_url}/admin/mentors", headers=headers)
            
            if response.status_code == 403:
                self.log_result("Admin Dashboard API", "Non-Admin Access Rejection", True)
            else:
                self.log_result("Admin Dashboard API", "Non-Admin Access Rejection", False, f"Expected 403, got {response.status_code}")
        except Exception as e:
            self.log_result("Admin Dashboard API", "Non-Admin Access Rejection", False, str(e))
        
        # Test 3: Verify mentor (need to get mentor ID first)
        try:
            # First get the mentor user data to get ID
            headers = {"Authorization": f"Bearer {self.tokens.get('mentor', '')}"}
            response = self.session.get(f"{self.base_url}/users/me", headers=headers)
            
            if response.status_code == 200:
                mentor_user = response.json()
                mentor_id = mentor_user.get("id")
                
                # Now verify the mentor as admin
                admin_headers = {"Authorization": f"Bearer {self.tokens.get('admin', '')}"}
                verify_response = self.session.put(f"{self.base_url}/admin/mentors/{mentor_id}/verify", headers=admin_headers)
                
                if verify_response.status_code == 200:
                    self.log_result("Admin Dashboard API", "Mentor Verification", True)
                else:
                    self.log_result("Admin Dashboard API", "Mentor Verification", False, f"Status: {verify_response.status_code}, Response: {verify_response.text}")
            else:
                self.log_result("Admin Dashboard API", "Mentor Verification", False, "Could not get mentor ID")
        except Exception as e:
            self.log_result("Admin Dashboard API", "Mentor Verification", False, str(e))
    
    def test_mentor_search(self):
        """Test Mentor Search API"""
        print("\n🔍 Testing Mentor Search API...")
        
        # Test 1: Search for mentors with Python skill
        try:
            headers = {"Authorization": f"Bearer {self.tokens.get('seeker', '')}"}
            params = {"q": "Python"}
            response = self.session.get(f"{self.base_url}/search/mentors", params=params, headers=headers)
            
            if response.status_code == 200:
                results = response.json()
                if isinstance(results, list):
                    self.log_result("Mentor Search API", "Search by Skill (Python)", True)
                else:
                    self.log_result("Mentor Search API", "Search by Skill (Python)", False, "Invalid response format")
            else:
                self.log_result("Mentor Search API", "Search by Skill (Python)", False, f"Status: {response.status_code}, Response: {response.text}")
        except Exception as e:
            self.log_result("Mentor Search API", "Search by Skill (Python)", False, str(e))
        
        # Test 2: Search for mentors with React skill
        try:
            headers = {"Authorization": f"Bearer {self.tokens.get('seeker', '')}"}
            params = {"q": "React"}
            response = self.session.get(f"{self.base_url}/search/mentors", params=params, headers=headers)
            
            if response.status_code == 200:
                results = response.json()
                self.log_result("Mentor Search API", "Search by Skill (React)", True)
            else:
                self.log_result("Mentor Search API", "Search by Skill (React)", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Mentor Search API", "Search by Skill (React)", False, str(e))
        
        # Test 3: Search with mentor name
        try:
            headers = {"Authorization": f"Bearer {self.tokens.get('seeker', '')}"}
            params = {"q": "Alex"}
            response = self.session.get(f"{self.base_url}/search/mentors", params=params, headers=headers)
            
            if response.status_code == 200:
                results = response.json()
                self.log_result("Mentor Search API", "Search by Name", True)
            else:
                self.log_result("Mentor Search API", "Search by Name", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Mentor Search API", "Search by Name", False, str(e))
        
        # Test 4: Search with bio content
        try:
            headers = {"Authorization": f"Bearer {self.tokens.get('seeker', '')}"}
            params = {"q": "software engineer"}
            response = self.session.get(f"{self.base_url}/search/mentors", params=params, headers=headers)
            
            if response.status_code == 200:
                results = response.json()
                self.log_result("Mentor Search API", "Search by Bio Content", True)
            else:
                self.log_result("Mentor Search API", "Search by Bio Content", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Mentor Search API", "Search by Bio Content", False, str(e))
    
    def test_chat_system(self):
        """Test Real-time Chat System"""
        print("\n💬 Testing Real-time Chat System...")
        
        # Test 1: Create conversation between seeker and mentor
        try:
            # First get mentor ID
            headers = {"Authorization": f"Bearer {self.tokens.get('mentor', '')}"}
            response = self.session.get(f"{self.base_url}/users/me", headers=headers)
            
            if response.status_code == 200:
                mentor_user = response.json()
                mentor_id = mentor_user.get("id")
                
                # Create conversation as seeker
                seeker_headers = {"Authorization": f"Bearer {self.tokens.get('seeker', '')}"}
                conv_response = self.session.post(f"{self.base_url}/conversations", 
                                                params={"mentor_id": mentor_id}, 
                                                headers=seeker_headers)
                
                if conv_response.status_code == 200:
                    conversation = conv_response.json()
                    self.conversations["main"] = conversation
                    self.log_result("Real-time Chat System", "Create Conversation", True)
                else:
                    self.log_result("Real-time Chat System", "Create Conversation", False, f"Status: {conv_response.status_code}, Response: {conv_response.text}")
            else:
                self.log_result("Real-time Chat System", "Create Conversation", False, "Could not get mentor ID")
        except Exception as e:
            self.log_result("Real-time Chat System", "Create Conversation", False, str(e))
        
        # Test 2: Get conversations list
        try:
            headers = {"Authorization": f"Bearer {self.tokens.get('seeker', '')}"}
            response = self.session.get(f"{self.base_url}/conversations", headers=headers)
            
            if response.status_code == 200:
                conversations = response.json()
                if isinstance(conversations, list):
                    self.log_result("Real-time Chat System", "Get Conversations List", True)
                else:
                    self.log_result("Real-time Chat System", "Get Conversations List", False, "Invalid response format")
            else:
                self.log_result("Real-time Chat System", "Get Conversations List", False, f"Status: {response.status_code}")
        except Exception as e:
            self.log_result("Real-time Chat System", "Get Conversations List", False, str(e))
        
        # Test 3: Send message in conversation
        try:
            if "main" in self.conversations:
                conversation_id = self.conversations["main"]["id"]
                message_data = {
                    "conversation_id": conversation_id,
                    "content": "Hi Alex! I'm interested in learning more about Python development. Could you help me understand best practices for web development?"
                }
                
                headers = {"Authorization": f"Bearer {self.tokens.get('seeker', '')}"}
                response = self.session.post(f"{self.base_url}/messages", json=message_data, headers=headers)
                
                if response.status_code == 200:
                    message = response.json()
                    self.log_result("Real-time Chat System", "Send Message", True)
                else:
                    self.log_result("Real-time Chat System", "Send Message", False, f"Status: {response.status_code}, Response: {response.text}")
            else:
                self.log_result("Real-time Chat System", "Send Message", False, "No conversation available")
        except Exception as e:
            self.log_result("Real-time Chat System", "Send Message", False, str(e))
        
        # Test 4: Get messages from conversation
        try:
            if "main" in self.conversations:
                conversation_id = self.conversations["main"]["id"]
                headers = {"Authorization": f"Bearer {self.tokens.get('seeker', '')}"}
                response = self.session.get(f"{self.base_url}/conversations/{conversation_id}/messages", headers=headers)
                
                if response.status_code == 200:
                    messages = response.json()
                    if isinstance(messages, list):
                        self.log_result("Real-time Chat System", "Get Messages", True)
                    else:
                        self.log_result("Real-time Chat System", "Get Messages", False, "Invalid response format")
                else:
                    self.log_result("Real-time Chat System", "Get Messages", False, f"Status: {response.status_code}")
            else:
                self.log_result("Real-time Chat System", "Get Messages", False, "No conversation available")
        except Exception as e:
            self.log_result("Real-time Chat System", "Get Messages", False, str(e))
        
        # Test 5: Send reply as mentor
        try:
            if "main" in self.conversations:
                conversation_id = self.conversations["main"]["id"]
                reply_data = {
                    "conversation_id": conversation_id,
                    "content": "Hello Sarah! I'd be happy to help you with Python development. Let's start with understanding the fundamentals of web frameworks like FastAPI and Flask. What's your current experience level?"
                }
                
                headers = {"Authorization": f"Bearer {self.tokens.get('mentor', '')}"}
                response = self.session.post(f"{self.base_url}/messages", json=reply_data, headers=headers)
                
                if response.status_code == 200:
                    self.log_result("Real-time Chat System", "Send Reply Message", True)
                else:
                    self.log_result("Real-time Chat System", "Send Reply Message", False, f"Status: {response.status_code}")
            else:
                self.log_result("Real-time Chat System", "Send Reply Message", False, "No conversation available")
        except Exception as e:
            self.log_result("Real-time Chat System", "Send Reply Message", False, str(e))
    
    def test_socket_io_connectivity(self):
        """Test Socket.IO connectivity"""
        print("\n🔌 Testing Socket.IO Connectivity...")
        
        try:
            # Create Socket.IO client
            sio_client = socketio.SimpleClient()
            
            # Connect to Socket.IO server
            socket_url = BACKEND_URL.replace('/api', '')
            sio_client.connect(socket_url, transports=['websocket'])
            
            if sio_client.connected:
                self.log_result("Real-time Chat System", "Socket.IO Connection", True)
                
                # Test joining a room
                if "main" in self.conversations:
                    room_data = {"room": self.conversations["main"]["id"]}
                    sio_client.emit("join_room", room_data)
                    self.log_result("Real-time Chat System", "Socket.IO Join Room", True)
                
                sio_client.disconnect()
            else:
                self.log_result("Real-time Chat System", "Socket.IO Connection", False, "Could not connect")
                
        except Exception as e:
            self.log_result("Real-time Chat System", "Socket.IO Connection", False, str(e))
    
    def run_all_tests(self):
        """Run all backend tests"""
        print("🚀 Starting Testnet Backend API Testing...")
        print(f"Backend URL: {self.base_url}")
        print("=" * 60)
        
        # Run tests in order
        self.test_user_authentication()
        self.test_profile_management()
        self.test_admin_dashboard()
        self.test_mentor_search()
        self.test_chat_system()
        self.test_socket_io_connectivity()
        
        # Print summary
        self.print_summary()
    
    def print_summary(self):
        """Print test results summary"""
        print("\n" + "=" * 60)
        print("📊 TEST RESULTS SUMMARY")
        print("=" * 60)
        
        total_passed = 0
        total_failed = 0
        
        for category, results in self.test_results.items():
            passed = results["passed"]
            failed = results["failed"]
            total_passed += passed
            total_failed += failed
            
            status = "✅ WORKING" if failed == 0 else "❌ ISSUES FOUND"
            print(f"\n{category}: {status}")
            print(f"  Passed: {passed}, Failed: {failed}")
            
            if results["errors"]:
                print("  Errors:")
                for error in results["errors"]:
                    print(f"    - {error}")
        
        print(f"\n🎯 OVERALL RESULTS:")
        print(f"Total Tests Passed: {total_passed}")
        print(f"Total Tests Failed: {total_failed}")
        print(f"Success Rate: {(total_passed / (total_passed + total_failed) * 100):.1f}%")
        
        if total_failed == 0:
            print("\n🎉 ALL BACKEND TESTS PASSED! The API is working correctly.")
        else:
            print(f"\n⚠️  {total_failed} tests failed. Please review the errors above.")

if __name__ == "__main__":
    tester = TestnetAPITester()
    tester.run_all_tests()
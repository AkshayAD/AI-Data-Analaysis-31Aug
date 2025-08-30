"""
Authentication and Authorization System
"""
import hashlib
import secrets
from datetime import datetime, timedelta
from typing import Dict, Optional, List
import json
import os

class User:
    def __init__(self, email: str, password_hash: str, role: str, 
                 name: str, team: str = None, skills: List[str] = None):
        self.email = email
        self.password_hash = password_hash
        self.role = role  # 'manager', 'associate', 'analyst'
        self.name = name
        self.team = team
        self.skills = skills or []
        self.created_at = datetime.now()
        self.last_login = None
        self.active_tasks = []
        self.completed_tasks = []
        
    def to_dict(self):
        return {
            'email': self.email,
            'role': self.role,
            'name': self.name,
            'team': self.team,
            'skills': self.skills,
            'last_login': self.last_login.isoformat() if self.last_login else None,
            'active_tasks': len(self.active_tasks),
            'completed_tasks': len(self.completed_tasks)
        }

class AuthenticationManager:
    def __init__(self):
        self.users_db = {}
        self.sessions = {}
        self.session_timeout = timedelta(hours=8)
        self._initialize_demo_users()
        
    def _initialize_demo_users(self):
        """Create demo users for testing"""
        demo_users = [
            {
                'email': 'manager@company.com',
                'password': 'manager123',
                'role': 'manager',
                'name': 'Sarah Johnson',
                'team': 'Analytics',
                'skills': ['strategy', 'planning', 'leadership']
            },
            {
                'email': 'analyst@company.com',
                'password': 'analyst123',
                'role': 'analyst',
                'name': 'Mike Chen',
                'team': 'Analytics',
                'skills': ['python', 'sql', 'machine_learning', 'statistics']
            },
            {
                'email': 'associate@company.com',
                'password': 'associate123',
                'role': 'associate',
                'name': 'Emily Davis',
                'team': 'Analytics',
                'skills': ['data_cleaning', 'visualization', 'reporting']
            },
            {
                'email': 'senior@company.com',
                'password': 'senior123',
                'role': 'analyst',
                'name': 'David Kim',
                'team': 'Analytics',
                'skills': ['python', 'sql', 'deep_learning', 'nlp', 'time_series']
            }
        ]
        
        for user_data in demo_users:
            self.register_user(
                email=user_data['email'],
                password=user_data['password'],
                role=user_data['role'],
                name=user_data['name'],
                team=user_data['team'],
                skills=user_data['skills']
            )
    
    def _hash_password(self, password: str) -> str:
        """Hash password with salt"""
        salt = "ai_platform_2024"
        return hashlib.sha256(f"{password}{salt}".encode()).hexdigest()
    
    def register_user(self, email: str, password: str, role: str, 
                     name: str, team: str = None, skills: List[str] = None) -> bool:
        """Register a new user"""
        if email in self.users_db:
            return False
        
        password_hash = self._hash_password(password)
        user = User(email, password_hash, role, name, team, skills)
        self.users_db[email] = user
        return True
    
    def authenticate(self, email: str, password: str) -> Optional[str]:
        """Authenticate user and create session"""
        if email not in self.users_db:
            return None
        
        user = self.users_db[email]
        password_hash = self._hash_password(password)
        
        if user.password_hash != password_hash:
            return None
        
        # Create session
        session_token = secrets.token_urlsafe(32)
        self.sessions[session_token] = {
            'email': email,
            'created_at': datetime.now(),
            'expires_at': datetime.now() + self.session_timeout
        }
        
        user.last_login = datetime.now()
        return session_token
    
    def validate_session(self, session_token: str) -> Optional[User]:
        """Validate session and return user"""
        if session_token not in self.sessions:
            return None
        
        session = self.sessions[session_token]
        
        if datetime.now() > session['expires_at']:
            del self.sessions[session_token]
            return None
        
        email = session['email']
        return self.users_db.get(email)
    
    def logout(self, session_token: str) -> bool:
        """Logout user by removing session"""
        if session_token in self.sessions:
            del self.sessions[session_token]
            return True
        return False
    
    def get_user_by_role(self, role: str) -> List[User]:
        """Get all users with specific role"""
        return [user for user in self.users_db.values() if user.role == role]
    
    def get_team_members(self, team: str) -> List[User]:
        """Get all users in a team"""
        return [user for user in self.users_db.values() if user.team == team]
    
    def find_best_analyst_for_task(self, required_skills: List[str]) -> Optional[User]:
        """Find analyst with best skill match"""
        analysts = self.get_user_by_role('analyst')
        associates = self.get_user_by_role('associate')
        candidates = analysts + associates
        
        if not candidates:
            return None
        
        # Score candidates by skill match and workload
        best_candidate = None
        best_score = -1
        
        for candidate in candidates:
            skill_match = len(set(required_skills) & set(candidate.skills))
            workload_factor = 1 / (len(candidate.active_tasks) + 1)
            score = skill_match * workload_factor
            
            if score > best_score:
                best_score = score
                best_candidate = candidate
        
        return best_candidate
    
    def assign_task_to_user(self, email: str, task_id: str) -> bool:
        """Assign task to user"""
        if email not in self.users_db:
            return False
        
        user = self.users_db[email]
        user.active_tasks.append(task_id)
        return True
    
    def complete_user_task(self, email: str, task_id: str) -> bool:
        """Mark task as completed for user"""
        if email not in self.users_db:
            return False
        
        user = self.users_db[email]
        if task_id in user.active_tasks:
            user.active_tasks.remove(task_id)
            user.completed_tasks.append(task_id)
            return True
        return False
    
    def get_user_workload(self, email: str) -> Dict:
        """Get user's current workload"""
        if email not in self.users_db:
            return {}
        
        user = self.users_db[email]
        return {
            'active_tasks': len(user.active_tasks),
            'completed_tasks': len(user.completed_tasks),
            'total_tasks': len(user.active_tasks) + len(user.completed_tasks)
        }

# Global auth manager instance
auth_manager = AuthenticationManager()
AI Study Planner - User Guide
Your Personal AI-Powered Study Assistant
🎯 What is This?
AI Study Planner is a smart app that creates personalized study schedules for your exams. Just tell it your subjects, marks, and exam dates - it calculates exactly how many hours to study each subject using artificial intelligence.
🚀 Quick Start (2 Minutes)

Step 1: Open the App
Run streamlit run app.py in your terminal


Step 2: Choose Your Mode
Table
Mode	Best For
🤖 Chatbot	Quick, natural conversation
📊 Scheduler	Manual detailed input
💬 Using the Chatbot (Easiest)
1. Start Chatting
Click "🤖 Chatbot" → Type your subjects naturally:
"I have Math, Physics and Chemistry"
2. Answer Questions
The bot will ask for each subject:
Marks (0-100) and Difficulty (1-5)
Format: 85, 4 means 85 marks, difficulty 4/5
3. Exam Dates
Tell how many days left for each exam:
"3" (means 3 days left)
4. Daily Hours
Enter hours you can study per day:
"6" (6 hours daily)
5. Get Your Plan!
View your personalized schedule with:
Hours allocated per subject
Priority scores
Visual charts
📈 Tracking Your Progress
After getting your plan, scroll down to see:
Progress Tracker Features:
Table
Feature	How to Use
🔥 Streak Counter	Log daily to build your streak
⏰ Today's Hours	Enter hours studied per subject
📝 Study Notes	Write what you studied (optional)
✅ Quick Log	Click "Log" to save your progress
Example Logging:
plain
Copy
Math: 2.5 hours → Notes: "Solved Chapter 3 problems"
Physics: 1.5 hours → Notes: "Revision of formulas"
🔄 Missed a Day? No Problem!
Option 1: Reschedule
Click "🔄 Reschedule Missed to Tomorrow"
Automatically redistributes missed hours
Option 2: Mark All Done
Click "✅ Mark All as Complete"
If you studied but forgot to log
📊 Understanding Your Results
Priority Score Explained:
plain
Copy
Priority = (100 - Your Marks) + Urgency + Difficulty

Higher Score = More Hours Allocated
Table
Subject	Marks	Days Left	Difficulty	Priority	Hours
Math	60	3	5	HIGH	3.2h
Physics	75	5	3	Medium	1.8h
Chemistry	90	10	2	Low	1.0h
Why? Math is urgent (3 days) + you're weak (60 marks) + it's hard (5/5)
💡 Tips for Success
Table
Do This	Why It Helps
✅ Be honest about difficulty	Better priority calculation
✅ Log daily	Maintains streak & motivation
✅ Use rescheduling	Don't let backlog grow
✅ Check suggestions	Personalized improvement tips
✅ Study high-priority first	Maximum exam score improvement
🎮 Features You'll Love
Table
Feature	What It Does
Natural Chat	Talk like texting a friend
Smart Priorities	AI decides what to study first
Streak Gamification	Stay motivated with daily streaks
Visual Charts	See your progress beautifully
Auto-Reschedule	Adapts when life happens
Personalized Tips	Knows your weak/strong subjects
❓ Common Questions
Q: Do I need to create an account?
No! Everything is saved on your computer automatically.
Q: Can I use this offline?
Yes, once installed it works without internet.
Q: What if my exam is tomorrow?
The AI will give that subject maximum hours automatically!
Q: Can I change my plan mid-week?
Yes! Just generate a new plan with updated info.
Q: Where is my data stored?
Locally in data/progress.json - only you can see it.
🆘 Need Help?
Table
Problem	Fix
App won't open	Check Python is installed
Charts not showing	Wait a few seconds, or refresh
Progress not saving	Check data/ folder exists
Wrong subject detected	Use simple names like "Math" not "Mathematics"
🎯 Remember
"Plan smarter. Study better. Stress less."
Let the AI handle the planning - you focus on studying!
Start your first study plan now! 🚀📚

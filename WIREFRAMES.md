# Wireframes - AI Communication Engine

## Document Overview
This document provides visual wireframes for the AI Communication Engine user interfaces, showing the layout, components, and user interactions for key screens.

**Design System:**
- **Primary Color:** Cyan (#06b6d4)
- **Background:** Dark slate (#0f172a, #1e293b)
- **Status Colors:** 
  - High Priority: Red (#ef4444)
  - Normal Priority: Blue (#3b82f6)
  - Needs Review: Orange (#f97316)
  - Success: Green (#22c55e)
- **Font:** JetBrains Mono (monospace)

---

## 1. Main Dashboard (Desktop View)

### Layout Overview
```
┌─────────────────────────────────────────────────────────────────────────────────────┐
│                        🎯 AI COMMAND CENTER                                          │
│                                                                        [👤 David M.] │
├─────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                      │
│  ┌───────────────────────────────────────────┐  ┌───────────────────────────────┐  │
│  │  📊 SYSTEM STATUS                          │  │  🎤 NEW VOICE REQUEST        │  │
│  │                                            │  │                               │  │
│  │  ● ACTIVE STREAMS: 3/50                   │  │  ┌─────────────────────────┐ │  │
│  │  ● PENDING TASKS: 12                      │  │  │    [  🎤 RECORD  ]      │ │  │
│  │  ● IN PROGRESS: 8                         │  │  │                         │ │  │
│  │  ● COMPLETED TODAY: 47                    │  │  │   Click to start        │ │  │
│  │                                            │  │  │   recording             │ │  │
│  │  Last Update: 2s ago ⚡                    │  │  └─────────────────────────┘ │  │
│  └───────────────────────────────────────────┘  │                               │  │
│                                                  │  or                           │  │
│  ┌───────────────────────────────────────────┐  │  [ 📁 Upload Audio File ]    │  │
│  │  🔍 FILTERS & SEARCH                       │  └───────────────────────────────┘  │
│  │                                            │                                     │
│  │  [All Departments ▼] [All Status ▼]       │  ┌───────────────────────────────┐  │
│  │  [🔍 Search tasks...]                     │  │  📢 LIVE FEED               │  │
│  │                                            │  │                               │  │
│  │  Show: [x] High Priority Only             │  │  > Room 305: Towels needed    │  │
│  │        [ ] Urgent Last Hour                │  │    2 min ago - In Progress    │  │
│  │        [ ] Unassigned                      │  │                               │  │
│  └───────────────────────────────────────────┘  │  > Room 412: AC not working   │  │
│                                                  │    5 min ago - Assigned       │  │
│  ┌──────────────────────────────────────────────────────────────────────────────┐  │
│  │  🎯 ACTIVE TASKS                                                    [Sort ▼] │  │
│  ├──────────────────────────────────────────────────────────────────────────────┤  │
│  │                                                                              │  │
│  │  ┌────────────────────────────────────────────────────────────────────────┐ │  │
│  │  │ 🔴 HIGH PRIORITY                                      [View] [Assign]   │ │  │
│  │  │ Room 201 - Maintenance Request                                         │ │  │
│  │  │ "Leak under the sink, water pooling on floor"                         │ │  │
│  │  │ 📍 Room 201  |  👤 John (Maintenance)  |  ⏱ 12 min ago               │ │  │
│  │  │ Status: IN PROGRESS  |  Priority: 5/5  |  🎧 1:35                     │ │  │
│  │  └────────────────────────────────────────────────────────────────────────┘ │  │
│  │                                                                              │  │
│  │  ┌────────────────────────────────────────────────────────────────────────┐ │  │
│  │  │ 🔵 NORMAL PRIORITY                                    [View] [Assign]   │ │  │
│  │  │ Room 305 - Housekeeping Request                                        │ │  │
│  │  │ "Need extra towels and toiletries"                                    │ │  │
│  │  │ 📍 Room 305  |  👤 Maria (Housekeeping)  |  ⏱ 8 min ago              │ │  │
│  │  │ Status: PENDING  |  Priority: 3/5  |  🎧 0:42                         │ │  │
│  │  └────────────────────────────────────────────────────────────────────────┘ │  │
│  │                                                                              │  │
│  │  ┌────────────────────────────────────────────────────────────────────────┐ │  │
│  │  │ 🟠 NEEDS REVIEW                                       [View] [Assign]   │ │  │
│  │  │ Room 412 - Ambiguous Request                                           │ │  │
│  │  │ "Something is broken" (Confidence: 45%)                               │ │  │
│  │  │ 📍 Room 412  |  👤 Unassigned  |  ⏱ 3 min ago                         │ │  │
│  │  │ Status: PENDING  |  Priority: ?  |  🎧 0:28                           │ │  │
│  │  └────────────────────────────────────────────────────────────────────────┘ │  │
│  │                                                                              │  │
│  │  [ Load More Tasks... ]                                                     │  │
│  └──────────────────────────────────────────────────────────────────────────────┘  │
│                                                                                      │
└─────────────────────────────────────────────────────────────────────────────────────┘
```

### Key Interactive Elements:
1. **System Status Panel** (Top Left)
   - Real-time counter updates via SSE
   - Green pulse animation on active streams
   - Clickable for detailed system health

2. **Voice Recording Widget** (Top Right)
   - Large, prominent record button
   - Visual feedback: waveform animation during recording
   - Alternative file upload option

3. **Live Feed** (Right Column)
   - Scrolling list of recent activities
   - Auto-updates in real-time
   - Click to jump to task details

4. **Task Cards**
   - Color-coded borders (red/blue/orange)
   - Inline audio player with waveform
   - Quick actions: View, Assign, Complete
   - Hover shows additional options

5. **Filters & Search**
   - Dropdown filters for department and status
   - Real-time search with debounce
   - Quick filter checkboxes

---

## 2. Task Detail Modal

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  ◀ Back to Dashboard                              [×] Close                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  TASK #1247 - Maintenance Request               🔴 HIGH PRIORITY     │  │
│  │  Created: Feb 19, 2026 2:45 PM                                       │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  🎧 AUDIO TRANSCRIPTION                                              │  │
│  │  ┌──────────────────────────────────────────────────────────────┐   │  │
│  │  │  [▶] ▬▬▬▬▬▬▬▬▬━━━━━━━━━━━━━━━━━━━━━━  0:42 / 1:35  [🔊]       │   │  │
│  │  └──────────────────────────────────────────────────────────────┘   │  │
│  │                                                                       │  │
│  │  "Hi, this is front desk. We have a guest in Room 201 reporting a   │  │
│  │   leak under the bathroom sink. Water is pooling on the floor.      │  │
│  │   They need this fixed urgently. Please send maintenance ASAP."     │  │
│  │                                                                       │  │
│  │  Confidence: 94% ✓  |  Language: English  |  Source: Phone Call     │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  🧠 AI ANALYSIS                                                      │  │
│  │                                                                       │  │
│  │  Intent:           Maintenance Request (Confidence: 96%)             │  │
│  │  Priority:         5/5 - URGENT                                      │  │
│  │  Department:       Maintenance                                       │  │
│  │  Room:            201                                               │  │
│  │  Urgency Keywords: "urgently", "ASAP", "pooling"                    │  │
│  │  Required Items:   [ Plumbing tools, Towels ]                       │  │
│  │                                                                       │  │
│  │  Priority Factors:                                                   │  │
│  │    • Urgency Level: ████████░░ 80%                                   │  │
│  │    • Inventory:     ██████░░░░ 60%                                   │  │
│  │    • Time Sensitive: ██████████ 100%                                 │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  👤 ASSIGNMENT                                                       │  │
│  │                                                                       │  │
│  │  Assigned To:  [John Martinez ▼]                                    │  │
│  │               (Maintenance - Available - Skills: Plumbing ✓)         │  │
│  │                                                                       │  │
│  │  Status:      [In Progress ▼]                                       │  │
│  │                                                                       │  │
│  │  [ 🔔 Send Notification ]   [ 📞 Call Assignee ]                    │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  📝 ACTIVITY TIMELINE                                                │  │
│  │                                                                       │  │
│  │  ● 2:45 PM - Task created by Sarah (Front Desk)                     │  │
│  │  ● 2:46 PM - Auto-assigned to John Martinez                         │  │
│  │  ● 2:47 PM - John acknowledged task                                 │  │
│  │  ● 2:48 PM - Status changed to "In Progress"                        │  │
│  │  ● 2:52 PM - Note added: "On my way to room 201"                    │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  💬 ADD NOTE                                                         │  │
│  │  ┌────────────────────────────────────────────────────────────────┐ │  │
│  │  │                                                                  │ │  │
│  │  │  Type update or comment...                                      │ │  │
│  │  │                                                                  │ │  │
│  │  └────────────────────────────────────────────────────────────────┘ │  │
│  │                                                                       │  │
│  │  [📸 Add Photo]  [🎤 Voice Note]            [ Cancel ]  [ Save ]    │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
│  ┌──────────────────────────────────────────────────────────────────────┐  │
│  │  [ ✓ Mark Complete ]  [ ⚠ Escalate ]  [ ↻ Reassign ]  [ × Delete ] │  │
│  └──────────────────────────────────────────────────────────────────────┘  │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Interactive Components:
1. **Audio Player**
   - Playback controls with seek bar
   - Speed controls (0.5x, 1x, 1.5x, 2x)
   - Download original audio file

2. **AI Analysis Section**
   - Visual bars showing confidence levels
   - Editable fields (manual override)
   - Expandable for more details

3. **Assignment Controls**
   - Dropdown with staff availability indicators
   - Quick notification buttons
   - Direct call integration

4. **Activity Timeline**
   - Chronological event log
   - User attribution
   - Timestamps relative or absolute

5. **Action Buttons**
   - Primary: Mark Complete (green)
   - Secondary: Escalate, Reassign
   - Danger: Delete (confirmation required)

---

## 3. Voice Recording Interface (Mobile View)

```
┌─────────────────────────────────┐
│  ≡  AI Command Center      [🔔] │
├─────────────────────────────────┤
│                                  │
│       📊 QUICK STATUS           │
│   ┌─────────────────────────┐  │
│   │  Active: 3    Today: 47 │  │
│   │  Pending: 12  Done: 8   │  │
│   └─────────────────────────┘  │
│                                  │
│                                  │
│   🎤 NEW VOICE REQUEST          │
│  ┌───────────────────────────┐ │
│  │                           │ │
│  │                           │ │
│  │      ┌─────────────┐     │ │
│  │      │             │     │ │
│  │      │             │     │ │
│  │      │      🎤      │     │ │
│  │      │             │     │ │
│  │      │   RECORD    │     │ │
│  │      │             │     │ │
│  │      │             │     │ │
│  │      └─────────────┘     │ │
│  │                           │ │
│  │    Tap to start           │ │
│  │                           │ │
│  └───────────────────────────┘ │
│                                  │
│                                  │
│  ┌───────────────────────────┐ │
│  │  📁 UPLOAD AUDIO FILE     │ │
│  └───────────────────────────┘ │
│                                  │
├─────────────────────────────────┤
│  [ 📋 Tasks ] [ 🎯 Active ]    │
│  [ 📊 Reports ] [ ⚙ Settings ]  │
└─────────────────────────────────┘
```

### Recording State (Active):
```
┌─────────────────────────────────┐
│  ◀ Cancel           Recording  │
├─────────────────────────────────┤
│                                  │
│   🔴 RECORDING                  │
│                                  │
│  ┌───────────────────────────┐ │
│  │                           │ │
│  │       ░░░░░░░░░░░░░       │ │
│  │     ░░░░░░░░░░░░░░░░░     │ │
│  │   ░░░░░    🔴    ░░░░░   │ │
│  │     ░░░░░░░░░░░░░░░░░     │ │
│  │       ░░░░░░░░░░░░░       │ │
│  │                           │ │
│  │  ▂▄▆█▆▄▂▄▆█▆▄▂▄▆█▆▄▂     │ │
│  │                           │ │
│  │       00:23 / 02:00       │ │
│  │                           │ │
│  └───────────────────────────┘ │
│                                  │
│  ┌───────────────────────────┐ │
│  │   "Hi, this is room 305.  │ │
│  │    We need extra towels   │ │
│  │    and..."                 │ │
│  └───────────────────────────┘ │
│    Real-time transcription     │
│                                  │
│  ┌─────────────────────────┐  │
│  │    [■ STOP & SEND]      │  │
│  └─────────────────────────┘  │
│                                  │
│  [ Pause ]                      │
│                                  │
└─────────────────────────────────┘
```

### Key Mobile Features:
1. **Large Touch Targets**
   - Minimum 48x48px buttons
   - Spacing for fat-finger friendliness
   - Clear visual feedback on tap

2. **Real-Time Transcription**
   - Shows preview as you speak
   - Builds confidence in accuracy
   - Can stop early if looks wrong

3. **Waveform Visualization**
   - Indicates audio is being captured
   - Visual confirmation of voice levels
   - Helpful for noisy environments

4. **Timer Display**
   - Current time / Maximum time
   - Warning at 1:45 remaining
   - Auto-stop at 2:00 limit

---

## 4. Task List View (Mobile)

```
┌─────────────────────────────────┐
│  ≡  My Tasks            🔍 [🔔] │
├─────────────────────────────────┤
│                                  │
│  [All] [Pending] [In Progress]  │
│                                  │
│                                  │
│  ┌───────────────────────────┐ │
│  │ 🔴 URGENT        2:45 PM  │ │
│  │                           │ │
│  │ Room 201 - Maintenance    │ │
│  │ "Leak under sink..."      │ │
│  │                           │ │
│  │ 👤 John M.  ⏱ 12 min ago  │ │
│  │                           │ │
│  │ [ ▶ START ]    [ VIEW ]  │ │
│  └───────────────────────────┘ │
│  │ Swipe → to complete       │ │
│  └───────────────────────────┘ │
│                                  │
│  ┌───────────────────────────┐ │
│  │ 🔵 NORMAL        2:37 PM  │ │
│  │                           │ │
│  │ Room 305 - Housekeeping   │ │
│  │ "Extra towels needed"     │ │
│  │                           │ │
│  │ 👤 Maria S.  ⏱ 8 min ago  │ │
│  │                           │ │
│  │ [ ▶ START ]    [ VIEW ]  │ │
│  └───────────────────────────┘ │
│                                  │
│  ┌───────────────────────────┐ │
│  │ 🟢 COMPLETED     1:15 PM  │ │
│  │                           │ │
│  │ Room 412 - Room Service   │ │
│  │ "Coffee and pastries"     │ │
│  │                           │ │
│  │ 👤 Lisa K.  ✓ 35 min ago  │ │
│  │                           │ │
│  │ [ ℹ VIEW DETAILS ]        │ │
│  └───────────────────────────┘ │
│                                  │
│  ┌───────────────────────────┐ │
│  │ 🔵 NORMAL        11:22 AM │ │
│  │                           │ │
│  │ Room 508 - Maintenance    │ │
│  │ "Light bulb replacement"  │ │
│  │                           │ │
│  │ 👤 Unassigned             │ │
│  │                           │ │
│  │ [ ✋ TAKE TASK ]           │ │
│  └───────────────────────────┘ │
│                                  │
│    [ Load More... ]             │
│                                  │
├─────────────────────────────────┤
│  ┌───────────────────────────┐ │
│  │   🎤 QUICK RECORD         │ │
│  └───────────────────────────┘ │
│                                  │
└─────────────────────────────────┘
```

### Mobile Task List Features:
1. **Swipe Gestures**
   - Swipe right → Mark complete
   - Swipe left → Reassign/Options
   - Visual feedback during swipe

2. **Status Tabs**
   - Quick filter by status
   - Badge count on each tab
   - Maintains scroll position

3. **Compact Card Design**
   - Essential info only
   - Room number prominent
   - Truncated descriptions
   - Tap card for full details

4. **Quick Actions**
   - START button (changes to IN PROGRESS)
   - VIEW button (opens detail modal)
   - TAKE TASK for unassigned

5. **Floating Action Button**
   - Always-accessible record button
   - Sticks to bottom of screen
   - Primary action for staff

---

## 5. Notification Panel

```
┌─────────────────────────────────────────────────────────────┐
│  🔔 NOTIFICATIONS (7 unread)                    [Mark All Read] │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  TODAY                                                       │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ 🔴 NEW URGENT TASK                    2 min ago        │ │
│  │                                                         │ │
│  │ Room 201 - Maintenance leak assigned to you            │ │
│  │ Priority: HIGH | Due: ASAP                             │ │
│  │                                                         │ │
│  │ [ View Task ]  [ Acknowledge ]                         │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ 🟠 ESCALATION ALERT                   15 min ago  ✓    │ │
│  │                                                         │ │
│  │ Task #1240 unacknowledged for 15 minutes               │ │
│  │ Room 412 - AC not working                              │ │
│  │                                                         │ │
│  │ [ Take Ownership ]  [ Reassign ]                       │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ 🟢 TASK COMPLETED                     32 min ago  ✓    │ │
│  │                                                         │ │
│  │ John completed: Room 305 housekeeping                  │ │
│  │ Duration: 18 minutes                                   │ │
│  │                                                         │ │
│  │ [ View Details ]  [ Dismiss ]                          │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ 🔵 NEW ASSIGNMENT                     1 hour ago  ✓    │ │
│  │                                                         │ │
│  │ You've been assigned: Room 508 - Light bulb            │ │
│  │ Priority: NORMAL | Due: Today 6 PM                     │ │
│  │                                                         │ │
│  │ [ View Task ]  [ Decline ]                             │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  YESTERDAY                                                   │
│                                                              │
│  ┌────────────────────────────────────────────────────────┐ │
│  │ 💬 COMMENT ADDED                      Yesterday  ✓     │ │
│  │                                                         │ │
│  │ Sarah commented on Task #1235:                         │ │
│  │ "Guest checked out, can close this"                    │ │
│  │                                                         │ │
│  │ [ View Task ]                                          │ │
│  └────────────────────────────────────────────────────────┘ │
│                                                              │
│  [ Load Older Notifications... ]                            │
│                                                              │
└─────────────────────────────────────────────────────────────┘
```

### Notification Features:
1. **Priority-Based Styling**
   - Red border: Urgent tasks
   - Orange: Escalations
   - Green: Completions
   - Blue: Normal updates

2. **Grouped by Date**
   - Today, Yesterday, This Week, Older
   - Chronological within groups
   - Collapse/expand date groups

3. **Inline Actions**
   - Quick actions without leaving panel
   - One-tap acknowledge
   - View task opens in modal overlay

4. **Read/Unread States**
   - Bold text for unread
   - Checkmark (✓) for read
   - Auto-mark read after 5 seconds view

---

## 6. Admin Settings Panel

```
┌─────────────────────────────────────────────────────────────────┐
│  ⚙ SYSTEM SETTINGS                                              │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────┐  ┌──────────────────────────────┐   │
│  │  📋 MENU             │  │  👥 STAFF MANAGEMENT          │   │
│  │                      │  │                               │   │
│  │  • Staff Management  │  │  ┌─────────────────────────┐ │   │
│  │  • Departments       │  │  │ 🔍 Search staff...      │ │   │
│  │  • Inventory         │  │  └─────────────────────────┘ │   │
│  │  • Webhooks          │  │                               │   │
│  │  • Notification      │  │  [ + Add New Staff Member ]  │   │
│  │    Rules             │  │                               │   │
│  │  • Security          │  │  ┌─────────────────────────┐ │   │
│  │  • Backup & Restore  │  │  │ John Martinez           │ │   │
│  │  • API Keys          │  │  │ Department: Maintenance │ │   │
│  │  • Audit Logs        │  │  │ Status: 🟢 Available    │ │   │
│  │                      │  │  │ Skills: Plumbing, HVAC  │ │   │
│  │                      │  │  │ [Edit] [Deactivate]     │ │   │
│  │                      │  │  └─────────────────────────┘ │   │
│  │                      │  │                               │   │
│  │                      │  │  ┌─────────────────────────┐ │   │
│  │                      │  │  │ Maria Santos            │ │   │
│  │                      │  │  │ Department: Housekeeping│ │   │
│  │                      │  │  │ Status: 🟡 Busy         │ │   │
│  │                      │  │  │ Skills: Cleaning, Laun. │ │   │
│  │                      │  │  │ [Edit] [Deactivate]     │ │   │
│  │                      │  │  └─────────────────────────┘ │   │
│  │                      │  │                               │   │
│  │                      │  │  ┌─────────────────────────┐ │   │
│  │                      │  │  │ Sarah Lee               │ │   │
│  │                      │  │  │ Department: Front Desk  │ │   │
│  │                      │  │  │ Status: 🔴 Off Duty     │ │   │
│  │                      │  │  │ Skills: Guest Relations │ │   │
│  │                      │  │  │ [Edit] [Deactivate]     │ │   │
│  │                      │  │  └─────────────────────────┘ │   │
│  │                      │  │                               │   │
│  └──────────────────────┘  └──────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

### Edit Staff Modal:
```
┌─────────────────────────────────────────────┐
│  EDIT STAFF MEMBER                   [×]   │
├─────────────────────────────────────────────┤
│                                              │
│  Name: [John Martinez         ]            │
│                                              │
│  Email: [john.m@hotel.com     ]            │
│                                              │
│  Phone: [+1 555-0123          ]            │
│                                              │
│  Department: [Maintenance ▼]               │
│                                              │
│  Skills: (Select all that apply)            │
│    [x] Plumbing                             │
│    [x] HVAC                                 │
│    [ ] Electrical                           │
│    [x] General Repair                       │
│    [ ] Carpentry                            │
│                                              │
│  Notification Preferences:                  │
│    Primary:   [Push Notifications ▼]       │
│    Secondary: [SMS ▼]                       │
│                                              │
│  Availability Schedule:                     │
│    Monday-Friday: [8:00 AM - 5:00 PM]      │
│    [ ] Available 24/7                       │
│                                              │
│  Current Status:                            │
│    ● Available                              │
│    ○ Busy                                   │
│    ○ Off Duty                               │
│                                              │
│  [ Cancel ]               [ Save Changes ]  │
│                                              │
└─────────────────────────────────────────────┘
```

---

## 7. Analytics Dashboard

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  📊 ANALYTICS & REPORTS                      [Export CSV] [Print]          │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  Date Range: [Last 7 Days ▼]    Department: [All ▼]                        │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  📈 KEY METRICS                                                        │ │
│  │                                                                         │ │
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌───────────┐ │ │
│  │  │  Total Tasks │  │   Completed  │  │   Avg Time   │  │   On-Time │ │ │
│  │  │     247      │  │     219      │  │   18.5 min   │  │    94.2%  │ │ │
│  │  │  ↑ 12% ▲    │  │  ↑ 8% ▲     │  │  ↓ 2.3m ▼   │  │  ↑ 1.5% ▲│ │ │
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └───────────┘ │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  📊 TASK VOLUME BY DAY                                                 │ │
│  │                                                                         │ │
│  │   50 │                                                                 │ │
│  │      │                                                        █        │ │
│  │   40 │                               █                        █        │ │
│  │      │              █                █                █       █        │ │
│  │   30 │      █       █        █       █                █       █        │ │
│  │      │      █       █        █       █        █       █       █        │ │
│  │   20 │      █       █        █       █        █       █       █        │ │
│  │      │  █   █   █   █   █    █   █   █   █    █   █   █   █   █       │ │
│  │   10 │  █   █   █   █   █    █   █   █   █    █   █   █   █   █       │ │
│  │      ├──┼───┼───┼───┼───┼────┼───┼───┼───┼────┼───┼───┼───┼───┤      │ │
│  │    0 └──┴───┴───┴───┴───┴────┴───┴───┴───┴────┴───┴───┴───┴───┘      │ │
│  │         Mon  Tue  Wed  Thu  Fri  Sat  Sun                              │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
│  ┌──────────────────────────────────────┐  ┌─────────────────────────────┐ │
│  │  🏢 TASK BREAKDOWN BY DEPARTMENT     │  │  ⏱ AVG COMPLETION TIME      │ │
│  │                                       │  │                             │ │
│  │  Housekeeping     ████████░ 42%     │  │  Housekeeping    12 min     │ │
│  │  Maintenance      ██████░░░ 28%     │  │  Maintenance     24 min     │ │
│  │  Room Service     ████░░░░░ 18%     │  │  Room Service    8 min      │ │
│  │  Front Desk       ██░░░░░░░ 8%      │  │  Front Desk      15 min     │ │
│  │  Concierge        █░░░░░░░░ 4%      │  │  Concierge       20 min     │ │
│  │                                       │  │                             │ │
│  └──────────────────────────────────────┘  └─────────────────────────────┘ │
│                                                                              │
│  ┌────────────────────────────────────────────────────────────────────────┐ │
│  │  🏆 TOP PERFORMERS (This Week)                                         │ │
│  │                                                                         │ │
│  │  1. 🥇 Maria Santos (Housekeeping)    - 47 tasks, Avg: 11 min         │ │
│  │  2. 🥈 John Martinez (Maintenance)    - 38 tasks, Avg: 22 min         │ │
│  │  3. 🥉 Lisa Kim (Room Service)        - 35 tasks, Avg: 7 min          │ │
│  │  4.    David Chen (Concierge)         - 28 tasks, Avg: 18 min         │ │
│  │  5.    Sarah Lee (Front Desk)         - 22 tasks, Avg: 14 min         │ │
│  └────────────────────────────────────────────────────────────────────────┘ │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### Analytics Features:
1. **Time Period Selector**
   - Today, Last 7 days, Last 30 days, Custom range
   - Comparison to previous period
   - Trend indicators (↑↓)

2. **Key Metrics Cards**
   - Large, prominent numbers
   - Percentage change from previous period
   - Color-coded (green=good, red=needs attention)

3. **Visual Charts**
   - Bar charts for volume over time
   - Pie charts for distribution
   - Horizontal bars for comparisons

4. **Performance Leaderboard**
   - Encourages healthy competition
   - Shows both quantity and quality (avg time)
   - Medal icons for top 3

5. **Export Options**
   - CSV for further analysis
   - PDF for presentation
   - Print-friendly layout

---

## 8. User Flow Diagram

```
┌─────────────────────────────────────────────────────────────────────────┐
│                        USER JOURNEY: REPORT ISSUE                        │
├─────────────────────────────────────────────────────────────────────────┤
│                                                                          │
│   GUEST                    FRONT DESK              STAFF MEMBER         │
│                                                                          │
│     │                          │                        │               │
│     │    1. Call Front Desk    │                        │               │
│     │────────────────────────> │                        │               │
│     │                          │                        │               │
│     │                          │  2. Record/Transcribe  │               │
│     │                          │      (Automatic)       │               │
│     │                          │                        │               │
│     │                          │  3. AI Classifies      │               │
│     │                          │     Intent & Priority  │               │
│     │                          │                        │               │
│     │                          │  4. Create Task &      │               │
│     │                          │     Auto-Assign ───────┼──────────┐   │
│     │                          │                        │          │   │
│     │                          │                        │  5. Notification │
│     │                          │                        │ <────────┘   │
│     │                          │                        │               │
│     │                          │                        │  6. Acknowledge │
│     │                          │                        │               │
│     │                          │                        │  7. Start Task │
│     │                          │                        │               │
│     │                          │                        │  8. Work...   │
│     │                          │                        │               │
│     │                          │ <──────────────────────┤  9. Complete  │
│     │                          │    (Auto-notified)     │               │
│     │                          │                        │               │
│     │  10. Inform Guest        │                        │               │
│     │ <──────────────────────  │                        │               │
│     │                          │                        │               │
│     ▼                          ▼                        ▼               │
│                                                                          │
│   Total Time: ~15-20 minutes for typical maintenance task               │
│                                                                          │
└─────────────────────────────────────────────────────────────────────────┘
```

---

## 9. System Architecture Diagram (Visual)

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         AI COMMUNICATION ENGINE                              │
└─────────────────────────────────────────────────────────────────────────────┘
                                     │
                     ┌───────────────┼───────────────┐
                     │               │               │
                     ▼               ▼               ▼
          ┌──────────────┐  ┌──────────────┐  ┌──────────────┐
          │  VoIP Calls  │  │     SMS      │  │ Walkie-Talkie│
          │   (Twilio)   │  │   (Vonage)   │  │   Streams    │
          └──────┬───────┘  └──────┬───────┘  └──────┬───────┘
                 │                 │                 │
                 └────────┬────────┴────────┬────────┘
                          │                 │
                          ▼                 ▼
                 ┌─────────────────────────────────┐
                 │    WEBHOOK HANDLERS              │
                 │  • Signature Validation          │
                 │  • Rate Limiting                 │
                 │  • Stream Management (50 max)    │
                 └─────────────┬───────────────────┘
                               │
                               ▼
                 ┌─────────────────────────────────┐
                 │   TRANSCRIPTION SERVICE          │
                 │  • Hugging Face Whisper          │
                 │  • OpenAI Whisper                │
                 │  • 11+ Languages                 │
                 │  • Confidence Scoring            │
                 └─────────────┬───────────────────┘
                               │
                               ▼
                 ┌─────────────────────────────────┐
                 │   INTENT CLASSIFIER              │
                 │  • LLM (GPT-4 / LLaMA)          │
                 │  • Rule-based Fallback           │
                 │  • Entity Extraction             │
                 │  • Priority Calculation          │
                 └─────────────┬───────────────────┘
                               │
                               ▼
                 ┌─────────────────────────────────┐
                 │   TASK ACTION ENGINE             │
                 │  • Task Creation                 │
                 │  • Smart Assignment              │
                 │  • Priority Ranking              │
                 │  • Escalation Logic              │
                 └─────────────┬───────────────────┘
                               │
                ┌──────────────┼──────────────┐
                │              │              │
                ▼              ▼              ▼
      ┌────────────────┐  ┌────────────────┐  ┌────────────────┐
      │   NOTIFICATION │  │    DATABASE    │  │   WEB APP      │
      │    SERVICE     │  │   (SQLite)     │  │  (Dashboard)   │
      │                │  │                │  │                │
      │  • Push (FCM)  │  │  • Tasks       │  │  • Real-time   │
      │  • SMS (Twilio)│  │  • Staff       │  │    Updates     │
      │  • Email(SMTP) │  │  • Transcripts │  │  • SSE Events  │
      │  • Voice Call  │  │  • Inventory   │  │  • Mobile UI   │
      └────────────────┘  └────────────────┘  └────────────────┘
                │                                      ▲
                │                                      │
                ▼                                      │
           ┌─────────┐                         ┌──────────────┐
           │  STAFF  │                         │ MANAGERS &   │
           │ MEMBERS │                         │ SUPERVISORS  │
           └─────────┘                         └──────────────┘
```

---

## 10. Responsive Design Breakpoints

### Desktop (1920px+)
- Three-column layout
- Live feed on right side
- Full task cards with all details
- Large dashboard widgets

### Tablet (768px - 1919px)
- Two-column layout
- Collapsible live feed
- Compact task cards
- Scrollable content areas

### Mobile (< 768px)
- Single-column layout
- Bottom navigation bar
- Full-screen modals
- Floating action button
- Swipe gestures enabled
- Minimized filters (drawer)

---

## Design Tokens

### Colors
```
Background:
  - Primary: #0f172a (slate-950)
  - Secondary: #1e293b (slate-800)
  - Card: #334155 (slate-700)

Text:
  - Primary: #f8fafc (slate-50)
  - Secondary: #cbd5e1 (slate-300)
  - Muted: #64748b (slate-500)

Status:
  - Error/High: #ef4444 (red-500)
  - Warning/Review: #f97316 (orange-500)
  - Success: #22c55e (green-500)
  - Info/Normal: #3b82f6 (blue-500)
  - Primary/Active: #06b6d4 (cyan-500)
```

### Typography
```
Font Family: 'JetBrains Mono', monospace

Sizes:
  - Heading 1: 2.25rem (36px) - bold
  - Heading 2: 1.875rem (30px) - bold
  - Heading 3: 1.5rem (24px) - semibold
  - Body: 1rem (16px) - regular
  - Small: 0.875rem (14px) - regular
  - Caption: 0.75rem (12px) - regular
```

### Spacing
```
Base unit: 4px

Scale:
  - xs: 4px
  - sm: 8px
  - md: 16px
  - lg: 24px
  - xl: 32px
  - 2xl: 48px
  - 3xl: 64px
```

### Shadows
```
Card: 0 4px 6px -1px rgba(0, 0, 0, 0.3)
Elevated: 0 10px 15px -3px rgba(0, 0, 0, 0.4)
Glow-High: 0 0 20px rgba(239, 68, 68, 0.4)
Glow-Normal: 0 0 15px rgba(59, 130, 246, 0.3)
Glow-Review: 0 0 20px rgba(249, 115, 22, 0.5)
```

---

## Accessibility Features

### WCAG 2.1 AA Compliance
- Color contrast ratio ≥ 4.5:1 for text
- Focus indicators on all interactive elements
- Keyboard navigation support (Tab, arrows, Enter, Escape)
- Screen reader labels and ARIA attributes
- Skip navigation links
- Text resizing up to 200% without breaking layout

### High Contrast Mode
- Alternative color scheme for low vision users
- Simplified interface option
- Large text mode

### Voice Control
- Speech-to-text for task creation
- Voice commands for common actions
- Audio feedback for confirmations

---

## Progressive Web App (PWA) Features

```
┌─────────────────────────────────────┐
│  AI Command Center                   │
│                                      │
│  Install this app for:               │
│  ✓ Offline access to tasks           │
│  ✓ Push notifications                │
│  ✓ Faster loading                    │
│  ✓ Home screen shortcut              │
│                                      │
│  [ Install ]      [ Not Now ]        │
└─────────────────────────────────────┘
```

### Offline Capabilities:
- View previously loaded tasks
- Queue task updates for sync
- Cached audio files
- Service worker for asset caching

### Install Prompt:
- Appears after 3 visits or 1 week
- Dismissible with "Don't ask again"
- App icon on device home screen

---

## Animation & Micro-interactions

### Recording Animation
- Pulsing red circle during recording
- Waveform bars animate with audio levels
- Smooth fade transitions

### Task Card Interactions
- Hover: Subtle elevation increase
- Click: Brief scale-down feedback
- Status change: Color transition (0.3s)
- New task: Slide in from right

### Notification Badge
- Pulse on new notification
- Bounce on high-priority alert
- Fade out on dismiss

### Loading States
- Skeleton screens while fetching data
- Progress spinner for long operations
- Shimmer effect on loading cards

---

## Error States & Empty States

### Empty Task List:
```
┌─────────────────────────────────────┐
│                                      │
│           📋                         │
│                                      │
│    No tasks assigned yet             │
│                                      │
│  You'll see tasks here when          │
│  they're assigned to you.            │
│                                      │
│  [ 🎤 Record New Request ]           │
│                                      │
└─────────────────────────────────────┘
```

### Error State:
```
┌─────────────────────────────────────┐
│                                      │
│           ⚠️                         │
│                                      │
│    Failed to load tasks              │
│                                      │
│  Check your internet connection      │
│  and try again.                      │
│                                      │
│  [ Retry ]    [ Go Offline ]         │
│                                      │
└─────────────────────────────────────┘
```

### No Network:
```
┌─────────────────────────────────────┐
│  📡 OFFLINE MODE                     │
│                                      │
│  You're viewing cached data.         │
│  Changes will sync when online.      │
│                                      │
│  [ View Cached Tasks ]               │
└─────────────────────────────────────┘
```

---

## Implementation Priority

### Phase 1 (MVP - Weeks 1-4)
1. Main Dashboard (Desktop)
2. Voice Recording Interface
3. Task Detail View
4. Basic Notification System

### Phase 2 (Mobile - Weeks 5-8)
1. Responsive Mobile Layout
2. Mobile Task List
3. Touch Gestures
4. PWA Installation

### Phase 3 (Advanced - Weeks 9-12)
1. Analytics Dashboard
2. Admin Settings
3. Advanced Filters
4. Performance Optimization

### Phase 4 (Polish - Weeks 13-16)
1. Animations & Micro-interactions
2. Accessibility Improvements
3. Offline Mode
4. Edge Case Handling

---

**Last Updated:** February 19, 2026  
**Document Version:** 1.0  
**Design Tool:** Figma (wireframes exported to ASCII for documentation)  
**Prototype:** [Interactive Prototype Link Placeholder]

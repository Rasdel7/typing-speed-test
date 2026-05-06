import streamlit as st
import time
import random
import json
import os
import pandas as pd
import matplotlib.pyplot as plt
from datetime import datetime
import warnings
warnings.filterwarnings('ignore')

st.set_page_config(
    page_title="Typing Speed Test",
    page_icon="⌨️",
    layout="wide"
)

st.title("⌨️ Typing Speed Test")
st.markdown("Test your typing speed, accuracy and "
            "consistency. How fast can you type?")
st.markdown("---")

# Word lists by difficulty
EASY_WORDS = [
    "the", "be", "to", "of", "and", "a", "in", "that",
    "have", "it", "for", "not", "on", "with", "he", "as",
    "you", "do", "at", "this", "but", "his", "by", "from",
    "they", "we", "say", "her", "she", "or", "an", "will",
    "my", "one", "all", "would", "there", "their", "what",
    "so", "up", "out", "if", "about", "who", "get", "which"
]

MEDIUM_WORDS = [
    "python", "data", "science", "machine", "learning",
    "algorithm", "function", "variable", "database", "network",
    "software", "hardware", "program", "computer", "internet",
    "keyboard", "monitor", "practice", "develop", "student",
    "project", "github", "streamlit", "analysis", "training",
    "accuracy", "features", "predict", "cluster", "visual"
]

HARD_WORDS = [
    "cryptocurrency", "algorithm", "infrastructure",
    "implementation", "authentication", "asynchronous",
    "microservices", "containerization", "orchestration",
    "hyperparameter", "regularization", "dimensionality",
    "convolutional", "recurrent", "transformer",
    "backpropagation", "reinforcement", "optimization",
    "classification", "visualization"
]

SENTENCES = [
    "The quick brown fox jumps over the lazy dog",
    "Python is a versatile programming language used in data science",
    "Machine learning models learn patterns from training data",
    "Practice makes perfect when it comes to typing speed",
    "GitHub is essential for every software developer",
    "Data science combines statistics programming and domain knowledge",
    "Neural networks are inspired by the human brain structure",
    "Every great developer started as a complete beginner",
    "Building projects every day is the best way to learn",
    "The best time to start was yesterday the next best time is now"
]

# Leaderboard
LB_FILE = "typing_leaderboard.json"

def load_leaderboard():
    if os.path.exists(LB_FILE):
        with open(LB_FILE, 'r') as f:
            return json.load(f)
    return []

def save_leaderboard(lb):
    with open(LB_FILE, 'w') as f:
        json.dump(lb, f, indent=2)

def generate_text(difficulty, mode):
    if mode == "Sentences":
        return random.choice(SENTENCES)
    elif difficulty == "Easy":
        return ' '.join(random.choices(EASY_WORDS, k=20))
    elif difficulty == "Medium":
        return ' '.join(random.choices(MEDIUM_WORDS, k=15))
    else:
        return ' '.join(random.choices(HARD_WORDS, k=10))

def calculate_wpm(text, typed, elapsed):
    words    = len(text.split())
    minutes  = elapsed / 60
    wpm      = words / minutes if minutes > 0 else 0
    return round(wpm)

def calculate_accuracy(original, typed):
    if not typed:
        return 0
    orig_words  = original.split()
    typed_words = typed.strip().split()
    correct     = sum(
        1 for o, t in zip(orig_words, typed_words)
        if o == t
    )
    total = max(len(orig_words), len(typed_words))
    return round((correct / total) * 100, 1)

# Session state
defaults = {
    'test_started':   False,
    'start_time':     None,
    'test_text':      '',
    'test_complete':  False,
    'history':        [],
    'player_name':    ''
}
for k, v in defaults.items():
    if k not in st.session_state:
        st.session_state[k] = v

# Tabs
tab1, tab2, tab3 = st.tabs([
    "⌨️ Type Test",
    "🏆 Leaderboard",
    "📊 My Progress"
])

# Tab 1 — Typing Test
with tab1:
    if not st.session_state.test_started \
       and not st.session_state.test_complete:

        st.markdown("### ⚙️ Test Settings")
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            player_name = st.text_input(
                "Your name:",
                placeholder="Enter name"
            )
        with col2:
            difficulty = st.selectbox(
                "Difficulty:",
                ["Easy", "Medium", "Hard"]
            )
        with col3:
            mode = st.selectbox(
                "Mode:",
                ["Words", "Sentences"]
            )
        with col4:
            st.markdown("### 🎯 Average WPM")
            st.markdown("""
            - Beginner: 20–40
            - Average: 40–60
            - Good: 60–80
            - Fast: 80–100
            - Pro: 100+
            """)

        if st.button("🚀 Start Test", type="primary"):
            if not player_name.strip():
                st.warning("Please enter your name!")
            else:
                st.session_state.test_text    = \
                    generate_text(difficulty, mode)
                st.session_state.test_started = True
                st.session_state.start_time   = \
                    time.time()
                st.session_state.test_complete = False
                st.session_state.player_name   = \
                    player_name
                st.rerun()

    elif st.session_state.test_started \
         and not st.session_state.test_complete:

        test_text = st.session_state.test_text
        elapsed   = time.time() - \
                    st.session_state.start_time

        st.markdown("### 📝 Type the text below:")
        st.markdown(
            f"<div style='background:#1e1e2e; "
            f"padding:20px; border-radius:10px; "
            f"font-size:1.2em; line-height:1.8; "
            f"letter-spacing:0.05em'>"
            f"{test_text}"
            f"</div>",
            unsafe_allow_html=True
        )
        st.markdown("")

        typed = st.text_area(
            "Start typing here:",
            height=100,
            placeholder="Type the text above...",
            key="typing_input"
        )

        col1, col2, col3 = st.columns(3)
        live_wpm = calculate_wpm(
            test_text, typed, max(elapsed, 1))
        live_acc = calculate_accuracy(test_text, typed)

        col1.metric("⏱️ Time",     f"{elapsed:.0f}s")
        col2.metric("💨 Live WPM", f"{live_wpm}")
        col3.metric("🎯 Accuracy", f"{live_acc}%")

        if st.button("✅ Submit", type="primary"):
            final_elapsed = time.time() - \
                            st.session_state.start_time
            final_wpm     = calculate_wpm(
                test_text, typed,
                max(final_elapsed, 1)
            )
            final_acc     = calculate_accuracy(
                test_text, typed)

            st.session_state.test_started  = False
            st.session_state.test_complete = True

            result = {
                'name':     st.session_state.player_name,
                'wpm':      final_wpm,
                'accuracy': final_acc,
                'time':     round(final_elapsed),
                'date':     datetime.now().strftime(
                    '%Y-%m-%d %H:%M')
            }
            st.session_state.history.append(result)

            lb = load_leaderboard()
            lb.append(result)
            lb.sort(key=lambda x: -x['wpm'])
            save_leaderboard(lb[:50])
            st.rerun()

    elif st.session_state.test_complete:
        last = st.session_state.history[-1]
        wpm  = last['wpm']
        acc  = last['accuracy']

        if wpm >= 80:
            grade = "🔥 Lightning Fast!"
            color = "#2ecc71"
        elif wpm >= 60:
            grade = "💨 Great Speed!"
            color = "#f39c12"
        elif wpm >= 40:
            grade = "👍 Getting There!"
            color = "#3498db"
        else:
            grade = "📚 Keep Practicing!"
            color = "#e74c3c"

        st.balloons()
        st.markdown(
            f"<h2 style='text-align:center; "
            f"color:{color}'>{grade}</h2>",
            unsafe_allow_html=True
        )

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("WPM",      wpm)
        c2.metric("Accuracy", f"{acc}%")
        c3.metric("Time",     f"{last['time']}s")
        c4.metric("Player",
                  last['name'][:10])

        # WPM gauge
        fig, ax = plt.subplots(figsize=(8, 2.5))
        ranges  = [(0, 40, '#e74c3c', 'Beginner'),
                   (40, 60, '#f39c12', 'Average'),
                   (60, 80, '#3498db', 'Good'),
                   (80, 100, '#2ecc71', 'Fast'),
                   (100, 130, '#9b59b6', 'Pro')]
        for start, end, c, label in ranges:
            ax.barh(0.5, end - start,
                    left=start, height=0.4,
                    color=c, alpha=0.7)
            ax.text((start + end) / 2, 0.85,
                    label, ha='center',
                    fontsize=8, fontweight='bold')
        wpm_c = min(max(wpm, 0), 129)
        ax.annotate('',
                    xy=(wpm_c, 0.3),
                    xytext=(wpm_c, 0.05),
                    arrowprops=dict(
                        arrowstyle='->',
                        color='black', lw=2.5))
        ax.text(wpm_c, 0.0,
                f'YOU\n{wpm}', ha='center',
                fontsize=9, fontweight='bold')
        ax.set_title('Your WPM on the Scale',
                     fontsize=12, pad=10)
        ax.axis('off')
        plt.tight_layout()
        st.pyplot(fig)

        col1, col2 = st.columns(2)
        with col1:
            if st.button("🔄 Try Again",
                         type="primary"):
                st.session_state.test_complete = False
                st.session_state.test_started  = False
                st.rerun()
        with col2:
            if st.button("📊 View My Progress"):
                st.info("Check the My Progress tab!")

# Tab 2 — Leaderboard
with tab2:
    st.markdown("### 🏆 Top Typists")
    lb = load_leaderboard()

    if not lb:
        st.info("No scores yet. Take a test first!")
    else:
        df_lb = pd.DataFrame(lb)

        top3   = df_lb.head(3)
        medals = ["🥇", "🥈", "🥉"]
        cols   = st.columns(3)
        for i, (_, row) in enumerate(
            top3.iterrows()
        ):
            cols[i].metric(
                f"{medals[i]} {row['name']}",
                f"{row['wpm']} WPM",
                f"{row['accuracy']}% accuracy"
            )

        st.markdown("---")
        display = df_lb[
            ['name', 'wpm', 'accuracy',
             'time', 'date']
        ].copy()
        display.index = range(1, len(display) + 1)
        display.columns = [
            'Name', 'WPM', 'Accuracy %',
            'Time (s)', 'Date'
        ]
        st.dataframe(display,
                     use_container_width=True)

# Tab 3 — Progress
with tab3:
    st.markdown("### 📊 Your Progress")
    history = st.session_state.history

    if len(history) < 2:
        st.info("Complete at least 2 tests "
                "to see your progress!")
    else:
        df_h = pd.DataFrame(history)

        fig, axes = plt.subplots(
            1, 2, figsize=(12, 4))

        axes[0].plot(
            range(1, len(df_h) + 1),
            df_h['wpm'],
            color='#3498db',
            linewidth=2,
            marker='o',
            markersize=6
        )
        axes[0].fill_between(
            range(1, len(df_h) + 1),
            df_h['wpm'],
            alpha=0.15,
            color='#3498db'
        )
        axes[0].set_title('WPM Over Tests',
                           fontsize=12)
        axes[0].set_xlabel('Test Number')
        axes[0].set_ylabel('WPM')
        axes[0].grid(alpha=0.3)

        axes[1].plot(
            range(1, len(df_h) + 1),
            df_h['accuracy'],
            color='#2ecc71',
            linewidth=2,
            marker='o',
            markersize=6
        )
        axes[1].fill_between(
            range(1, len(df_h) + 1),
            df_h['accuracy'],
            alpha=0.15,
            color='#2ecc71'
        )
        axes[1].set_title('Accuracy Over Tests',
                           fontsize=12)
        axes[1].set_xlabel('Test Number')
        axes[1].set_ylabel('Accuracy %')
        axes[1].set_ylim(0, 105)
        axes[1].grid(alpha=0.3)

        plt.tight_layout()
        st.pyplot(fig)

        best_wpm = max(df_h['wpm'])
        avg_wpm  = df_h['wpm'].mean()
        best_acc = max(df_h['accuracy'])

        s1, s2, s3 = st.columns(3)
        s1.metric("Best WPM",   best_wpm)
        s2.metric("Average WPM", f"{avg_wpm:.0f}")
        s3.metric("Best Accuracy", f"{best_acc}%")

st.markdown("---")
st.markdown(
    "Built by **Jyotiraditya** | "
    "Typing Speed Test | "
    "Practice daily to improve!"
)
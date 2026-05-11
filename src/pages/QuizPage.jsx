import React, { useState } from "react";
import { useNavigate } from "react-router-dom";
import { useUser } from "../contexts/UserContext";
import {
  submitQuizResult,
  updateUserProgress as apiUpdateUserProgress,
} from "../services/api";

import letA from "../assets/A.png";
import letB from "../assets/B.png";
import letC from "../assets/C.png";
import letD from "../assets/D.png";
import letE from "../assets/E.png";
import letF from "../assets/F.png";
import letG from "../assets/G.png";
import letH from "../assets/H.png";
import letI from "../assets/I.png";
import letJ from "../assets/J.png";
import letK from "../assets/K.png";
import letL from "../assets/L.png";
import letM from "../assets/M.png";
import letN from "../assets/N.png";
import letO from "../assets/O.png";
import letP from "../assets/P.png";
import letQ from "../assets/Q.png";
import letR from "../assets/R.png";
import letS from "../assets/S.png";
import letT from "../assets/T.png";
import letU from "../assets/U.png";
import letV from "../assets/V.png";
import letW from "../assets/W.png";
import letX from "../assets/X.png";
import letY from "../assets/Y.png";
import letZ from "../assets/Z.png";

import num1 from "../assets/1.png";
import num2 from "../assets/2.png";
import num3 from "../assets/3.png";
import num4 from "../assets/4.png";
import num5 from "../assets/5.png";
import num6 from "../assets/6.png";
import num7 from "../assets/7.png";
import num8 from "../assets/8.png";
import num9 from "../assets/9.png";

import GoodDayGif from "../assets/good-day.gif";
import WhatIsThatGif from "../assets/what-is-that.gif";
import WhatTimeIsItGif from "../assets/what-time-is-it.gif";

const QuizPage = () => {
  const navigate = useNavigate();
  const { isAuthenticated, user, progress, updateProgress } = useUser();
  const [selectedQuiz, setSelectedQuiz] = useState(null);
  const [currentCard, setCurrentCard] = useState(0);
  const [score, setScore] = useState(0);
  const [showResult, setShowResult] = useState(false);

  const quizzes = [
    {
      id: 1,
      title: " Alphabet Quiz",
      description: "Test your knowledge of the JSL alphabet from A to Z",
      icon: "🔤",
      difficulty: "Beginner",
      questions: 26,
      flashcards: [
        { id: 1, image: letD, options: ["V", "A", "G", "D"], correct: 3 },
        { id: 2, image: letB, options: ["L", "F", "B", "H"], correct: 2 },
        { id: 3, image: letE, options: ["I", "E", "K", "P"], correct: 1 },
        { id: 4, image: letA, options: ["A", "G", "H", "S"], correct: 0 },
        { id: 5, image: letS, options: ["X", "E", "S", "O"], correct: 2 },
        { id: 6, image: letF, options: ["N", "F", "C", "U"], correct: 1 },
        { id: 7, image: letV, options: ["A", "O", "X", "V"], correct: 3 },
        { id: 8, image: letC, options: ["C", "Y", "I", "Q"], correct: 0 },
        { id: 9, image: letX, options: ["H", "F", "X", "L"], correct: 2 },
        { id: 10, image: letW, options: ["P", "W", "M", "D"], correct: 1 },
        { id: 11, image: letQ, options: ["I", "F", "K", "Q"], correct: 3 },
        { id: 12, image: letO, options: ["C", "O", "M", "L"], correct: 1 },
        { id: 13, image: letT, options: ["V", "A", "T", "U"], correct: 2 },
        { id: 14, image: letL, options: ["X", "V", "L", "Z"], correct: 2 },
        { id: 15, image: letH, options: ["R", "J", "Z", "H"], correct: 3 },
        { id: 16, image: letJ, options: ["J", "T", "Q", "P"], correct: 0 },
        { id: 17, image: letP, options: ["K", "E", "S", "P"], correct: 3 },
        { id: 18, image: letR, options: ["H", "G", "R", "S"], correct: 2 },
        { id: 19, image: letG, options: ["G", "F", "W", "L"], correct: 0 },
        { id: 20, image: letI, options: ["I", "J", "X", "H"], correct: 0 },
        { id: 21, image: letK, options: ["A", "H", "K", "D"], correct: 2 },
        { id: 22, image: letM, options: ["X", "J", "M", "H"], correct: 2 },
        { id: 23, image: letY, options: ["B", "Y", "D", "P"], correct: 1 },
        { id: 24, image: letZ, options: ["Y", "R", "J", "Z"], correct: 3 },
        { id: 25, image: letN, options: ["N", "M", "A", "Q"], correct: 0 },
        { id: 26, image: letU, options: ["H", "L", "U", "X"], correct: 2 },
      ],
    },
    {
      id: 2,
      title: " Numbers Quiz",
      description: "Test your knowledge of numbers 1-9 in JSL",
      icon: "🔢",
      difficulty: "Beginner",
      questions: 9,
      flashcards: [
        { id: 8, image: num8, options: ["2", "8", "5", "1"], correct: 1 },
        { id: 5, image: num5, options: ["3", "7", "2", "5"], correct: 3 },
        { id: 1, image: num1, options: ["1", "2", "3", "4"], correct: 0 },
        { id: 9, image: num9, options: ["4", "6", "9", "3"], correct: 2 },
        { id: 3, image: num3, options: ["8", "4", "3", "6"], correct: 2 },
        { id: 6, image: num6, options: ["6", "8", "1", "4"], correct: 0 },
        { id: 4, image: num4, options: ["4", "1", "9", "5"], correct: 0 },
        { id: 2, image: num2, options: ["5", "2", "7", "9"], correct: 1 },
        { id: 7, image: num7, options: ["9", "3", "7", "2"], correct: 2 },
      ],
    },
    {
      id: 3,
      title: " Basic Greetings Quiz",
      description: "Test your knowledge of common greetings and phrases",
      icon: "👋",
      difficulty: "Beginner",
      questions: 3,
      flashcards: [
        { id: 1, image: WhatTimeIsItGif, options: ["What time is it", "How are you?", "What is that?", "What is your name"], correct: 0 },
        { id: 2, image: GoodDayGif, options: ["Where are you?", "I am fine", "Good day", "How are you?"], correct: 2 },
        { id: 3, image: WhatIsThatGif, options: ["What are you doing?", "What time is it?", "Who are you?", "What is that?"], correct: 3 },
      ],
    },
    {
      id: 4,
      title: " JSL Vocabulary Quiz",
      description: "Test your knowledge of common JSL vocabulary words",
      icon: "📚",
      difficulty: "Beginner",
      questions: 15,
      flashcards: [
        { id: 1, image: " ", options: [""], correct: 0 },
        { id: 2, image: " ", options: [""], correct: 1 },
        { id: 3, image: " ", options: [""], correct: 0 },
      ],
    },
  ];

  const startQuiz = (quiz) => {
    setSelectedQuiz(quiz);
    setCurrentCard(0);
    setScore(0);
    setShowResult(false);
  };

  const handleAnswer = async (selectedIndex) => {
  
  
    const isCorrect =
      selectedIndex === selectedQuiz.flashcards[currentCard].correct;
    const newScore = isCorrect ? score + 1 : score;

    if (currentCard < selectedQuiz.flashcards.length - 1) {
      setScore(newScore);
      setCurrentCard(currentCard + 1);
    } else {
      console.log("Selected option index:");
      const finalScore = newScore;
      const percentageScore = Math.round(
        (finalScore / selectedQuiz.flashcards.length) * 100,
      );

      // Get current progress from Redux
      const currentQuizzes = progress?.quizzesTaken || 0;
      const currentAvgScore = progress?.averageScore || 0;

      // Calculate new values
      const newQuizzesTaken = currentQuizzes + 1;
      const newAverageScore = Math.round(
        (currentAvgScore * currentQuizzes + percentageScore) / newQuizzesTaken,
      );

      // Persist result and progress to backend
      const resultPayload = {
        quiz_name: selectedQuiz.title,
        score: finalScore,
        total: selectedQuiz.flashcards.length,
        percentage: percentageScore,
      };

      try {
        await submitQuizResult(resultPayload);
      } catch (err) {
        console.error("Failed to submit quiz result:", err);
      }

      const progressPayload = {
        quizzesTaken: newQuizzesTaken,
        averageScore: newAverageScore,
      };

      try {
        await apiUpdateUserProgress(progressPayload);
      } catch (err) {
        console.error("Failed to update user progress:", err);
      }

      // Update context
      updateProgress(progressPayload);

      setScore(finalScore);
      setShowResult(true);
    }
  };

  const backToQuizzes = () => {
    setSelectedQuiz(null);
    setCurrentCard(0);
    setScore(0);
    setShowResult(false);
  };

  // Show quiz list
  if (!selectedQuiz) {
    return (
      <div style={{ maxWidth: "56rem", margin: "0 auto", padding: "0 1rem" }}>
        <div style={{ textAlign: "center", marginBottom: "2rem" }}>
          <h1
            style={{
              fontSize: "2rem",
              fontWeight: "bold",
              marginBottom: "0.5rem",
            }}
          >
            📝 Practice Quizzes
          </h1>
          <p style={{ color: "#6b7280" }}>
            Choose a topic to test your knowledge and track your progress
          </p>
          {progress?.quizzesTaken > 0 && (
            <p
              style={{
                color: "#10b981",
                marginTop: "0.5rem",
                fontSize: "0.875rem",
              }}
            >
              ✅ You've completed {progress.quizzesTaken} quiz(zes) so far!
            </p>
          )}
        </div>

        <div style={{ display: "grid", gap: "1rem" }}>
          {quizzes.map((quiz) => (
            <div
              key={quiz.id}
              style={{
                background: "white",
                borderRadius: "1rem",
                padding: "1.5rem",
                boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                transition: "all 0.2s",
                border: "1px solid #e5e7eb",
                cursor: "pointer",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                gap: "1rem",
                flexWrap: "wrap",
              }}
              onClick={() => startQuiz(quiz)}
              onMouseEnter={(e) => {
                e.currentTarget.style.boxShadow =
                  "0 10px 15px -3px rgba(0, 0, 0, 0.1)";
                e.currentTarget.style.transform = "translateY(-2px)";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.boxShadow =
                  "0 4px 6px -1px rgba(0, 0, 0, 0.1)";
                e.currentTarget.style.transform = "translateY(0)";
              }}
            >
              <div style={{ flex: 1 }}>
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "0.75rem",
                    marginBottom: "0.5rem",
                  }}
                >
                  <span style={{ fontSize: "2rem" }}>{quiz.icon}</span>
                  <h2
                    style={{
                      fontSize: "1.25rem",
                      fontWeight: "bold",
                      margin: 0,
                    }}
                  >
                    {quiz.title}
                  </h2>
                  <span
                    style={{
                      padding: "0.25rem 0.75rem",
                      borderRadius: "9999px",
                      fontSize: "0.75rem",
                      fontWeight: "500",
                      background:
                        quiz.difficulty === "Beginner" ? "#d1fae5" : "#fef3c7",
                      color:
                        quiz.difficulty === "Beginner" ? "#065f46" : "#92400e",
                    }}
                  >
                    {quiz.difficulty}
                  </span>
                </div>
                <p
                  style={{
                    color: "#6b7280",
                    fontSize: "0.875rem",
                    marginBottom: "0.5rem",
                  }}
                >
                  {quiz.description}
                </p>
                <p style={{ color: "#9ca3af", fontSize: "0.75rem" }}>
                  {quiz.questions} questions
                </p>
              </div>
              <div>
                <button
                  style={{
                    padding: "0.5rem 1.5rem",
                    background: "#3b82f6",
                    color: "white",
                    border: "none",
                    borderRadius: "0.5rem",
                    cursor: "pointer",
                    fontWeight: "600",
                    fontSize: "0.875rem",
                    transition: "background 0.2s",
                  }}
                  onMouseEnter={(e) =>
                    (e.currentTarget.style.background = "#2563eb")
                  }
                  onMouseLeave={(e) =>
                    (e.currentTarget.style.background = "#3b82f6")
                  }
                >
                  Start Quiz →
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>
    );
  }

  // Show quiz results
  if (showResult) {
    const percentage = Math.round(
      (score / selectedQuiz.flashcards.length) * 100,
    );

    return (
      <div style={{ maxWidth: "28rem", margin: "0 auto" }}>
        <div
          style={{
            background: "white",
            borderRadius: "1rem",
            padding: "2rem",
            boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
            textAlign: "center",
          }}
        >
          <div style={{ fontSize: "4rem", marginBottom: "1rem" }}>🎉</div>
          <h2
            style={{
              fontSize: "1.5rem",
              fontWeight: "bold",
              marginBottom: "0.5rem",
            }}
          >
            {selectedQuiz.title} Complete!
          </h2>
          <p
            style={{
              fontSize: "2rem",
              fontWeight: "bold",
              color: "#3b82f6",
              marginBottom: "0.5rem",
            }}
          >
            {score}/{selectedQuiz.flashcards.length}
          </p>
          <p
            style={{
              fontSize: "1rem",
              color: "#6b7280",
              marginBottom: "0.5rem",
            }}
          >
            Score: {percentage}%
          </p>
          <p style={{ color: "#6b7280", marginBottom: "1.5rem" }}>
            {percentage === 100
              ? "Perfect score! You're an expert! 🌟"
              : percentage >= 70
                ? "Great job! Keep practicing to improve! 💪"
                : "Nice try! Review the material and try again! 📚"}
          </p>
          <div
            style={{ display: "flex", gap: "1rem", justifyContent: "center" }}
          >
            <button
              onClick={backToQuizzes}
              style={{
                padding: "0.5rem 1rem",
                background: "#6b7280",
                color: "white",
                border: "none",
                borderRadius: "0.5rem",
                cursor: "pointer",
                fontWeight: "600",
              }}
            >
              Back to Quizzes
            </button>
            <button
              onClick={() => startQuiz(selectedQuiz)}
              style={{
                padding: "0.5rem 1rem",
                background: "#3b82f6",
                color: "white",
                border: "none",
                borderRadius: "0.5rem",
                cursor: "pointer",
                fontWeight: "600",
              }}
            >
              Try Again
            </button>
          </div>
        </div>
      </div>
    );
  }

  // Show active quiz
  return (
    <div style={{ maxWidth: "42rem", margin: "0 auto" }}>
      <div
        style={{
          background: "white",
          borderRadius: "1rem",
          padding: "1.5rem",
          boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
        }}
      >
        <div
          style={{
            display: "flex",
            justifyContent: "space-between",
            marginBottom: "1rem",
            paddingBottom: "0.5rem",
            borderBottom: "1px solid #e5e7eb",
          }}
        >
          <div>
            <span style={{ fontSize: "0.875rem", color: "#6b7280" }}>
              {selectedQuiz.title}
            </span>
            <h3
              style={{
                fontSize: "1rem",
                fontWeight: "600",
                marginTop: "0.25rem",
              }}
            >
              Question {currentCard + 1} of {selectedQuiz.flashcards.length}
            </h3>
          </div>
          <span style={{ fontWeight: "600", color: "#3b82f6" }}>
            Score: {score}
          </span>
        </div>

        <div
          style={{
            display: "flex",
            justifyContent: "center",
            alignItems: "center",
            marginBottom: "1.5rem",
            background: "#f9fafb",
            borderRadius: "0.5rem",
            padding: "1rem",
          }}
        >
          <img
            src={selectedQuiz.flashcards[currentCard].image}
            alt="ASL sign"
            style={{
              maxWidth: "100%",
              maxHeight: "300px",
              width: "auto",
              height: "auto",
              objectFit: "contain",
              borderRadius: "0.5rem",
            }}
          />
        </div>

        <div
          style={{
            display: "grid",
            gridTemplateColumns: "repeat(2, 1fr)",
            gap: "1rem",
          }}
        >
          {selectedQuiz.flashcards[currentCard].options.map((option, index) => (
            <button
              key={index}
              onClick={() => handleAnswer(index)}
              style={{
                padding: "1rem",
                background: "#f3f4f6",
                border: "2px solid transparent",
                borderRadius: "0.5rem",
                fontSize: "1rem",
                fontWeight: "600",
                cursor: "pointer",
                transition: "all 0.2s",
              }}
              onMouseEnter={(e) => {
                e.currentTarget.style.background = "#dbeafe";
                e.currentTarget.style.borderColor = "#3b82f6";
              }}
              onMouseLeave={(e) => {
                e.currentTarget.style.background = "#f3f4f6";
                e.currentTarget.style.borderColor = "transparent";
              }}
            >
              {option}
            </button>
          ))}
        </div>

        <div style={{ marginTop: "1rem", textAlign: "center" }}>
          <button
            onClick={backToQuizzes}
            style={{
              padding: "0.5rem 1rem",
              background: "transparent",
              color: "#6b7280",
              border: "none",
              cursor: "pointer",
              fontSize: "0.875rem",
            }}
          >
            ← Back to Quizzes
          </button>
        </div>
      </div>
    </div>
  );
};

export default QuizPage;

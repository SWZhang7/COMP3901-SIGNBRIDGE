import React, { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { useUser } from "../contexts/UserContext";
import { getQuizResults } from "../services/api";

const ProfilePage = () => {
  const navigate = useNavigate();
  const { isAuthenticated, user, progress } = useUser();

  if (!isAuthenticated) {
    return (
      <div style={{ textAlign: "center", padding: "3rem 0" }}>
        <h2
          style={{
            fontSize: "1.5rem",
            fontWeight: "bold",
            marginBottom: "1rem",
          }}
        >
          Please Sign Up to View Profile
        </h2>
        <button onClick={() => navigate("/signup")} className="btn btn-primary">
          Sign Up Now
        </button>
      </div>
    );
  }

  const userData = {
    name: user?.name || "User",
    email: user?.email || "user@example.com",
    joinDate: user?.joinDate
      ? new Date(user.joinDate).toLocaleDateString()
      : "Just joined",
    stats: {
      quizzesTaken: progress?.quizzesTaken || 0,
      averageScore: progress?.averageScore || 0,
    },
  };

  // Calculate level progress based on quizzes taken
  const calculateProgress = () => {
    const quizzes = userData.stats.quizzesTaken;

    if (quizzes === 0) {
      return { beginner: 0, intermediate: 0, advanced: 0 };
    }

    if (quizzes <= 3) {
      return { beginner: (quizzes / 3) * 100, intermediate: 0, advanced: 0 };
    } else if (quizzes <= 7) {
      return {
        beginner: 100,
        intermediate: ((quizzes - 3) / 4) * 100,
        advanced: 0,
      };
    } else {
      return {
        beginner: 100,
        intermediate: 100,
        advanced: Math.min(((quizzes - 7) / 5) * 100, 100),
      };
    }
  };

  const levelProgress = calculateProgress();

  const getUserLevel = () => {
    const quizzes = userData.stats.quizzesTaken;
    if (quizzes === 0) return "Beginner";
    if (quizzes <= 3) return "Beginner";
    if (quizzes <= 7) return "Beginner";
    return "Beginner";
  };

  const currentLevel = getUserLevel();
  const [history, setHistory] = useState([]);

  useEffect(() => {
    let mounted = true;
    const loadHistory = async () => {
      try {
        const resp = await getQuizResults();
        if (!mounted) return;
        setHistory(resp.history || []);
      } catch (err) {
        console.error("Failed to load quiz history", err);
      }
    };
    if (isAuthenticated) loadHistory();
    return () => {
      mounted = false;
    };
  }, [isAuthenticated]);

  return (
    <div>
      {/* Welcome Message - only shows when no quizzes taken */}
      {userData.stats.quizzesTaken === 0 && (
        <div
          style={{
            background: "linear-gradient(135deg, #fef3c7 0%, #fde68a 100%)",
            borderRadius: "0.75rem",
            padding: "1.5rem",
            marginBottom: "1.5rem",
            textAlign: "center",
          }}
        >
          <h3
            style={{
              fontSize: "1.25rem",
              fontWeight: "bold",
              marginBottom: "0.5rem",
            }}
          >
            👋 Welcome to SignBridge, {userData.name}!
          </h3>
          <p style={{ color: "#92400e", marginBottom: "1rem" }}>
            Take your first quiz to start tracking your progress.
          </p>
          <button
            onClick={() => navigate("/quiz")}
            style={{
              padding: "0.5rem 1.5rem",
              background: "#f59e0b",
              color: "white",
              border: "none",
              borderRadius: "0.5rem",
              cursor: "pointer",
              fontWeight: "600",
            }}
          >
            Take Your First Quiz →
          </button>
        </div>
      )}

      {/* User Info Card */}
      <div
        style={{
          background: "white",
          borderRadius: "0.75rem",
          padding: "1.5rem",
          marginBottom: "1.5rem",
          boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
        }}
      >
        <div
          style={{
            display: "flex",
            alignItems: "center",
            gap: "1rem",
            flexWrap: "wrap",
          }}
        >
          <div
            style={{
              background: "linear-gradient(135deg, #3b82f6, #8b5cf6)",
              color: "white",
              width: "5rem",
              height: "5rem",
              borderRadius: "50%",
              display: "flex",
              alignItems: "center",
              justifyContent: "center",
              fontSize: "2rem",
              fontWeight: "bold",
            }}
          >
            {userData.name.charAt(0).toUpperCase()}
          </div>
          <div>
            <h2
              style={{
                fontSize: "1.5rem",
                fontWeight: "bold",
                marginBottom: "0.25rem",
              }}
            >
              {userData.name}
            </h2>
            <p style={{ color: "#6b7280", marginBottom: "0.5rem" }}>
              {userData.email}
            </p>
            <div style={{ display: "flex", gap: "1rem", flexWrap: "wrap" }}>
              <span
                style={{
                  background:
                    currentLevel === "Beginner"
                      ? "#d1fae5"
                      : currentLevel === "Intermediate"
                        ? "#fef3c7"
                        : "#fee2e2",
                  color:
                    currentLevel === "Beginner"
                      ? "#065f46"
                      : currentLevel === "Intermediate"
                        ? "#92400e"
                        : "#991b1b",
                  padding: "0.25rem 0.75rem",
                  borderRadius: "9999px",
                  fontSize: "0.875rem",
                }}
              >
                {currentLevel}
              </span>
              <span style={{ fontSize: "0.875rem", color: "#6b7280" }}>
                Member since {userData.joinDate}
              </span>
            </div>
          </div>
        </div>
      </div>

      {/* Stats Grid - 2 columns now */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(2, 1fr)",
          gap: "1rem",
          marginBottom: "1.5rem",
        }}
      >
        <div
          style={{
            background: "white",
            padding: "1.5rem",
            borderRadius: "0.5rem",
            textAlign: "center",
            boxShadow: "0 1px 3px 0 rgba(0, 0, 0, 0.1)",
          }}
        >
          <div
            style={{
              fontSize: "2rem",
              fontWeight: "bold",
              color: userData.stats.quizzesTaken === 0 ? "#9ca3af" : "#3b82f6",
            }}
          >
            {userData.stats.quizzesTaken}
          </div>
          <div style={{ color: "#6b7280" }}>Quizzes Taken</div>
        </div>

        <div
          style={{
            background: "white",
            padding: "1.5rem",
            borderRadius: "0.5rem",
            textAlign: "center",
            boxShadow: "0 1px 3px 0 rgba(0, 0, 0, 0.1)",
          }}
        >
          <div
            style={{
              fontSize: "2rem",
              fontWeight: "bold",
              color: userData.stats.averageScore === 0 ? "#9ca3af" : "#10b981",
            }}
          >
            {userData.stats.averageScore}%
          </div>
          <div style={{ color: "#6b7280" }}>Average Score</div>
        </div>
      </div>

      {/* Quiz History */}
      <div style={{ marginTop: "1.5rem" }}>
        <h3
          style={{
            fontSize: "1.125rem",
            fontWeight: "600",
            marginBottom: "0.75rem",
          }}
        >
          Recent Quizzes
        </h3>
        {history.length === 0 ? (
          <div style={{ color: "#6b7280" }}>
            No quiz history yet. Take a quiz to get started.
          </div>
        ) : (
          <div style={{ display: "grid", gap: "0.5rem" }}>
            {history.map((h) => (
              <div
                key={h.id}
                style={{
                  background: "white",
                  padding: "0.75rem",
                  borderRadius: "0.5rem",
                  display: "flex",
                  justifyContent: "space-between",
                  alignItems: "center",
                }}
              >
                <div>
                  <div style={{ fontWeight: 600 }}>{h.quiz_name}</div>
                  <div style={{ color: "#6b7280", fontSize: "0.875rem" }}>
                    {new Date(h.created_at).toLocaleString()}
                  </div>
                </div>
                <div style={{ textAlign: "right" }}>
                  <div style={{ fontWeight: 700, color: "#3b82f6" }}>
                    {h.score}/{h.total}
                  </div>
                  <div style={{ color: "#6b7280", fontSize: "0.875rem" }}>
                    {Math.round(h.percentage)}%
                  </div>
                </div>
              </div>
            ))}
          </div>
        )}
      </div>
    </div>
  );
};

export default ProfilePage;

import React from "react";
import { useUser } from "../contexts/UserContext";
import { useNavigate } from "react-router-dom";

const LearningPage = () => {
  const navigate = useNavigate();
  const { isAuthenticated } = useUser();

  const learningMaterials = [
    {
      id: 1,
      title: "🔤 Alphabet",
      description: "Learn the ASL alphabet from A to Z",
      topics: ["A-M", "N-Z"],
      resourceUrl: "#",
      difficulty: "Beginner",
    },
    {
      id: 2,
      title: "🔢 Numbers",
      description: "Master counting from 1 to 9 in JSL",
      topics: ["1-9"],
      resourceUrl: "#",
      difficulty: "Beginner",
    },
    {
      id: 3,
      title: "👋 Basic Greetings",
      description: "Essential everyday greetings and phrases",
      topics: [
        "Good day",
        "What is that",
        "What time is it",
      ],
      resourceUrl: "#",
      difficulty: "Beginner",
    },
    {
      id: 4,
      title: "📚 JSL Vocabulary",
      description: "Expand your vocabulary with common words and phrases",
      topics: ["Various Terms"],
      resourceUrl: "#",
      difficulty: "Beginner",
    },
  ];

  if (!isAuthenticated) {
    return (
      <div style={{ textAlign: "center", padding: "3rem 0" }}>
        <div
          style={{
            maxWidth: "28rem",
            margin: "0 auto",
            background: "white",
            borderRadius: "0.75rem",
            padding: "2rem",
            boxShadow: "0 10px 15px -3px rgba(0, 0, 0, 0.1)",
          }}
        >
          <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>📚</div>
        </div>
      </div>
    );
  }

  const getDifficultyClass = (difficulty) => {
    if (difficulty === "Beginner")
      return { background: "#d1fae5", color: "#065f46" };
    return { background: "#fef3c7", color: "#92400e" };
  };

  return (
    <div style={{ maxWidth: "56rem", margin: "0 auto", padding: "0 1rem" }}>
      {/* Page Header */}
      <div style={{ textAlign: "center", marginBottom: "2rem" }}>
        <h1
          style={{
            fontSize: "2rem",
            fontWeight: "bold",
            marginBottom: "0.5rem",
          }}
        >
          📖 Learning Resources
        </h1>
        <p style={{ color: "#6b7280" }}>
          Start your JSL journey with these foundational lessons
        </p>
      </div>

      {/* Learning Materials Grid */}
      <div style={{ display: "grid", gap: "1.5rem" }}>
        {learningMaterials.map((material) => {
          const difficultyStyle = getDifficultyClass(material.difficulty);

          return (
            <div
              key={material.id}
              style={{
                background: "white",
                borderRadius: "1rem",
                padding: "1.5rem",
                boxShadow: "0 4px 6px -1px rgba(0, 0, 0, 0.1)",
                transition: "all 0.2s",
                border: "1px solid #e5e7eb",
                display: "flex",
                justifyContent: "space-between",
                alignItems: "center",
                gap: "2rem",
                flexWrap: "wrap",
              }}
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
              {/* Left side - Content */}
              <div style={{ flex: 1 }}>
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: "0.75rem",
                    flexWrap: "wrap",
                    marginBottom: "0.75rem",
                  }}
                >
                  <h2
                    style={{
                      fontSize: "1.5rem",
                      fontWeight: "bold",
                      margin: 0,
                    }}
                  >
                    {material.title}
                  </h2>
                  <span
                    style={{
                      padding: "0.25rem 0.75rem",
                      borderRadius: "9999px",
                      fontSize: "0.75rem",
                      fontWeight: "500",
                      background: difficultyStyle.background,
                      color: difficultyStyle.color,
                    }}
                  >
                    {material.difficulty}
                  </span>
                </div>

                <p
                  style={{
                    color: "#6b7280",
                    marginBottom: "1rem",
                    lineHeight: "1.5",
                    fontSize: "1rem",
                  }}
                >
                  {material.description}
                </p>

                <div>
                  <p
                    style={{
                      fontSize: "0.875rem",
                      fontWeight: "500",
                      color: "#374151",
                      marginBottom: "0.5rem",
                    }}
                  >
                    What you'll learn:
                  </p>
                  <div
                    style={{ display: "flex", flexWrap: "wrap", gap: "0.5rem" }}
                  >
                    {material.topics.map((topic, index) => (
                      <span
                        key={index}
                        style={{
                          padding: "0.25rem 0.75rem",
                          background: "#f3f4f6",
                          borderRadius: "0.5rem",
                          fontSize: "0.875rem",
                          color: "#374151",
                        }}
                      >
                        {topic}
                      </span>
                    ))}
                  </div>
                </div>
              </div>

              {/* Right side - Centered Button */}
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  justifyContent: "center",
                  minWidth: "160px",
                }}
              >
                <button
                  onClick={() => navigate(`/learning/practice/${material.id}`)}
                  style={{
                    padding: "0.75rem 1.5rem",
                    background: "#10b981",
                    color: "white",
                    border: "none",
                    borderRadius: "0.5rem",
                    cursor: "pointer",
                    fontWeight: "600",
                    fontSize: "0.875rem",
                    transition: "background 0.2s",
                    whiteSpace: "nowrap",
                  }}
                  onMouseEnter={(e) =>
                    (e.currentTarget.style.background = "#059669")
                  }
                  onMouseLeave={(e) =>
                    (e.currentTarget.style.background = "#10b981")
                  }
                >
                  📄 Practice Sheet
                </button>
              </div>
            </div>
          );
        })}
      </div>

      {/* Quiz CTA */}
      <div
        style={{
          marginTop: "2rem",
          background: "linear-gradient(135deg, #eff6ff 0%, #e0e7ff 100%)",
          borderRadius: "1rem",
          padding: "1.5rem",
          textAlign: "center",
        }}
      >
        <h3
          style={{
            fontSize: "1.125rem",
            fontWeight: "bold",
            marginBottom: "0.5rem",
          }}
        >
          🎯 Test Your Knowledge
        </h3>
        <p style={{ color: "#374151", marginBottom: "1rem" }}>
          Take quizzes to see what you've learned and track your progress
        </p>
        <button
          onClick={() => navigate("/quiz")}
          style={{
            padding: "0.5rem 1.5rem",
            background: "#3b82f6",
            color: "white",
            border: "none",
            borderRadius: "0.5rem",
            cursor: "pointer",
            fontWeight: "600",
          }}
        >
          Go to Quizzes →
        </button>
      </div>
    </div>
  );
};

export default LearningPage;

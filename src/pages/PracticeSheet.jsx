import React from "react";
import { useParams, useNavigate } from "react-router-dom";

import A from "../assets/A.png";
import B from "../assets/B.png";
import C from "../assets/C.png";
import D from "../assets/D.png";
import E from "../assets/E.png";
import F from "../assets/F.png";
import G from "../assets/G.png";
import H from "../assets/H.png";
import I from "../assets/I.png";
import J from "../assets/J.png";
import K from "../assets/K.png";
import L from "../assets/L.png";
import M from "../assets/M.png";
import N from "../assets/N.png";
import O from "../assets/O.png";
import P from "../assets/P.png";
import Q from "../assets/Q.png";
import R from "../assets/R.png";
import S from "../assets/S.png";
import T from "../assets/T.png";
import U from "../assets/U.png";
import V from "../assets/V.png";
import W from "../assets/W.png";
import X from "../assets/X.png";
import Y from "../assets/Y.png";
import Z from "../assets/Z.png";

import One from "../assets/1.png";
import Two from "../assets/2.png";
import Three from "../assets/3.png";
import Four from "../assets/4.png";
import Five from "../assets/5.png";
import Six from "../assets/6.png";
import Seven from "../assets/7.png";
import Eight from "../assets/8.png";
import Nine from "../assets/9.png";

import GoodDayGif from "../assets/good-day.gif";
import WhatIsThatGif from "../assets/what-is-that.gif";
import WhatTimeIsItGif from "../assets/what-time-is-it.gif";

import Fallback from "../assets/asl-image.jpeg";

const IMAGE_MAP = {
  A,
  B,
  C,
  D,
  E,
  F,
  G,
  H,
  I,
  J,
  K,
  L,
  M,
  N,
  O,
  P,
  Q,
  R,
  S,
  T,
  U,
  V,
  W,
  X,
  Y,
  Z,
  1: One,
  2: Two,
  3: Three,
  4: Four,
  5: Five,
  6: Six,
  7: Seven,
  8: Eight,
  9: Nine,
  "GOOD DAY": GoodDayGif,
  "WHAT IS THAT": WhatIsThatGif,
  "WHAT TIME IS IT": WhatTimeIsItGif,
};

const SHEETS = {
  1: {
    title: "Alphabet Practice Sheet",
    description: "Practice the ASL alphabet A–Z. Trace and sign each letter.",
    items: [
      "A",
      "B",
      "C",
      "D",
      "E",
      "F",
      "G",
      "H",
      "I",
      "J",
      "K",
      "L",
      "M",
      "N",
      "O",
      "P",
      "Q",
      "R",
      "S",
      "T",
      "U",
      "V",
      "W",
      "X",
      "Y",
      "Z",
    ],
  },
  2: {
    title: "Numbers Practice Sheet",
    description: "Practice counting and signing numbers 1–9.",
    items: ["1", "2", "3", "4", "5", "6", "7", "8", "9"],
  },
  3: {
    title: "Basic Greetings Practice Sheet",
    description: "Common greetings and short phrases to practice.",
    items: [
       "GOOD DAY",
       "WHAT IS THAT",
       "WHAT TIME IS IT",
    ],
  },
  4: {
    title: "JSL Vocabulary Practice Sheet",
    description: "A collection of common JSL vocabulary to review.",
    items: ["Please", "Thank you", "Yes", "No", "Help"],
  },
};

const PracticeSheet = () => {
  const { id } = useParams();
  const navigate = useNavigate();
  const sheet = SHEETS[id] || null;

  if (!sheet) {
    return (
      <div
        style={{ maxWidth: "48rem", margin: "2rem auto", textAlign: "center" }}
      >
        <h2>Practice sheet not found</h2>
        <p>The requested practice sheet doesn't exist.</p>
        <button onClick={() => navigate(-1)} style={{ marginTop: "1rem" }}>
          Go back
        </button>
      </div>
    );
  }

  return (
    <div style={{ maxWidth: "56rem", margin: "2rem auto", padding: "0 1rem" }}>
      <div
        style={{
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <h1 style={{ margin: 0 }}>{sheet.title}</h1>
        <button onClick={() => navigate(-1)} style={{ padding: "0.5rem 1rem" }}>
          Back
        </button>
      </div>

      <p style={{ color: "#6b7280" }}>{sheet.description}</p>

      <div style={{ marginTop: "1.5rem", display: "grid", gap: "0.75rem" }}>
        {sheet.items.map((it, idx) => {
          const key = String(it).toUpperCase();
          const img = IMAGE_MAP[key] || IMAGE_MAP[String(it)] || Fallback;
          return (
            <div
              key={idx}
              style={{
                display: "flex",
                gap: "1rem",
                alignItems: "center",
                padding: "0.75rem",
                borderRadius: "0.5rem",
                background: "#fff",
                border: "1px solid #e5e7eb",
              }}
            >
              <img
                src={img}
                alt={it}
                style={{
                  width: 96,
                  height: 96,
                  objectFit: "contain",
                  borderRadius: 8,
                  background: "#f9fafb",
                }}
              />
              <div>
                <div style={{ fontSize: "1rem", fontWeight: 600 }}>{it}</div>
              </div>
            </div>
          );
        })}
      </div>
    </div>
  );
};

export default PracticeSheet;

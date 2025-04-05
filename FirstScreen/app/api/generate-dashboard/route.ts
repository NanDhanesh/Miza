// app/api/generate-dashboard/route.ts
import { NextRequest, NextResponse } from "next/server";

const GEMINI_API_KEY = process.env.GEMINI_API_KEY;
const GEMINI_API_URL = `https://generativelanguage.googleapis.com/v1/models/gemini-1.5-pro:generateContent?key=${GEMINI_API_KEY}`;

export async function POST(req: NextRequest) {
  try {
    const { prompt } = await req.json();

    if (!prompt) {
      return NextResponse.json({ error: "Prompt is required" }, { status: 400 });
    }

    if (!GEMINI_API_KEY) {
      return NextResponse.json({ error: "API key not configured" }, { status: 500 });
    }

    // Modify the prompt with JSON conversion instructions
    const modifiedPrompt = `Convert the following study plan into JSON with:
- "timer" (number of minutes)
- "checklist" (array of study tasks)
- "notes" (optional tips or motivation)

Study Plan: ${prompt}`;

    const response = await fetch(GEMINI_API_URL, {
      method: "POST",
      headers: {
        "Content-Type": "application/json",
      },
      body: JSON.stringify({
        contents: [
          {
            parts: [
              {
                text: modifiedPrompt, // Use the modified prompt
              },
            ],
          },
        ],
        generationConfig: {
          temperature: 0.7,
          maxOutputTokens: 250,
        },
      }),
    });

    if (!response.ok) {
      throw new Error(`Gemini API responded with status: ${response.status}`);
    }

    const data = await response.json();
    const generatedText = data.candidates[0].content.parts[0].text;

    return NextResponse.json({
      message: "Dashboard generated successfully",
      result: generatedText,
    });
  } catch (error) {
    console.error("Error generating dashboard:", error);
    return NextResponse.json(
      { error: "Failed to generate dashboard" },
      { status: 500 }
    );
  }
}
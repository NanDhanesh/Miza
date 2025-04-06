// app/focus-wrapped/page.tsx
"use client";

import { useSearchParams } from "next/navigation";
import FocusWrapped from "./focus-wrapped";

export default function FocusWrappedPage() {
  const searchParams = useSearchParams();

  // Extract checklist completion data from query parameters
  const completedTasks = parseInt(searchParams.get("completed") || "0");
  const totalTasks = parseInt(searchParams.get("total") || "1"); // Avoid division by 0
  const checklistPercentage = Math.round((completedTasks / totalTasks) * 100);

  const focusPercentage = parseInt(searchParams.get("focus") || "0");

  const overallScore = parseInt(searchParams.get("score") || "0");

  // Optional: User name (can be passed via query or fetched from user context if available)
//   const userName = searchParams.get("userName") || "there";

  return (
    <FocusWrapped
      focusPercentage={focusPercentage} // Use default value or hardcode as needed
      checklistPercentage={checklistPercentage} // Dynamically calculated
      overallScore={overallScore} // Use default value or hardcode as needed
      //totalFocusHours={124} // Use default value or hardcode as needed
    />
  );
}
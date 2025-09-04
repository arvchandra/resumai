import React, { createContext, useContext, useReducer } from "react";

import { useResumeApi } from "../api/resumeApi.ts";

import type { TailoredResume } from "../types/TailoredResume.ts";

interface TailoredResumesState {
  tailoredResumes: TailoredResume[];
  error: string;
}

interface TailoredResumesMethods {
  fetchTailoredResumes: () => Promise<void>;
  addNewTailoredResume: (tailoredResume: TailoredResume) => void;
}

const tailoredResumesInitialState: TailoredResumesState = {
  tailoredResumes: [],
  error: "",
}

type TailoredResumesContextType = TailoredResumesState & TailoredResumesMethods;

export const TailoredResumesContext = createContext<TailoredResumesContextType | undefined>(undefined)

type ResumesAction =
  | { type: "SET_TAILORED_RESUMES"; payload: TailoredResume[]; }
  | { type: "ADD_NEW_TAILORED_RESUME", payload: TailoredResume; }
  | { type: "SET_ERROR", payload: string; };

function tailoredResumesReducer(state: TailoredResumesState, action: ResumesAction) {
  if (action.type == "SET_TAILORED_RESUMES") {
    return {
      ...state,
      tailoredResumes: action.payload,
    }
  }
  if (action.type == "ADD_NEW_TAILORED_RESUME") {
    const newTailoredResumes = [...state.tailoredResumes];
    return {
      ...state,
      tailoredResumes: [action.payload, ...newTailoredResumes],
    }
  }
  if (action.type == "SET_ERROR") {
    return {
      ...state,
      error: action.payload,
    }
  }

  return state;
}

export const TailoredResumesContextProvider: React.FC<{ children: React.ReactNode }> = ({ children }) => {
  const [tailoredResumesState, tailoredResumesDispatch] = useReducer(tailoredResumesReducer, tailoredResumesInitialState);
  const { getTailoredUserResumes } = useResumeApi();

  const handleAddNewTailoredResume = (tailoredResume: TailoredResume) => {
    tailoredResumesDispatch({
      type: "ADD_NEW_TAILORED_RESUME",
      payload: tailoredResume,
    })
  };

  // Async tailored resumes fetching function
  const fetchTailoredResumes = async () => {
    try {
      const response = await getTailoredUserResumes();
      const data: TailoredResume[] = await response.json();
      tailoredResumesDispatch({ type: "SET_TAILORED_RESUMES", payload: data });
    } catch (error) {
      if (error instanceof Error) {
        tailoredResumesDispatch({ type: "SET_ERROR", payload: error.message });
      } else {
        tailoredResumesDispatch({ type: "SET_ERROR", payload: "An error occurred." });
      }
    }
  };

  const ctxValue = {
    tailoredResumes: tailoredResumesState.tailoredResumes,
    error: tailoredResumesState.error,
    fetchTailoredResumes,
    addNewTailoredResume: handleAddNewTailoredResume,
  }

  return (
    <TailoredResumesContext.Provider value={ctxValue} >
      {children}
    </TailoredResumesContext.Provider>
  )
}

export const useTailoredResumesContext = (): TailoredResumesContextType => {
  const context = useContext(TailoredResumesContext);
  if (!context) throw new Error("useTailoredResumesContext must be used within TailoredResumesContextProvider");
  return context;
};

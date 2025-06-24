import React, { createContext, useCallback, useReducer } from "react";

type ResumeContextType = {
  resumeName: string;
  updateResumeName: (name: string) => void;
}

// export const ResumeContext = createContext({
//   resumeName: '',
//   updateResumeName: (name: string) => {},
// });

export const ResumeContext = createContext<ResumeContextType>({
  resumeName: '',
  updateResumeName: () => {},
})

type ResumeState = {
  resumeName: string;
}

type ResumeAction = {type: "UPDATE_RESUME_NAME"; payload: string};

function resumeReducer(state: ResumeState, action: ResumeAction) {
  if (action.type == "UPDATE_RESUME_NAME") {
    return {
      resumeName: action.payload,
    }
  }

  return state;
}

interface ContextProviderProps {
  children: React.ReactNode;
}

export const ResumeContextProvider: React.FC<ContextProviderProps> = ({ children }) => {
  const [resumeState, resumeDispatch] = useReducer(resumeReducer, {
    resumeName: '',
  })

  const handleUpdateResumeName = useCallback((name: string) => {
    resumeDispatch({
      type: "UPDATE_RESUME_NAME",
      payload: name,
    })
  }, []);

  const ctxValue = {
    resumeName: resumeState.resumeName,
    updateResumeName: handleUpdateResumeName,
  }

  return (
    <ResumeContext.Provider value={ctxValue} >
      {children}
    </ResumeContext.Provider>
  )
}
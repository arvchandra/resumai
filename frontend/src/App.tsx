import { useEffect } from "react";

// import JobPosting from "./components/JobPosting/JobPosting";
import ResumeTailorForm from "./components/ResumeTailorForm/ResumeTailorForm";

import useFetch from "./hooks/useFetch";
import { useResumesContext } from "./contexts/ResumesContext";
import { fetchUserResumes } from "./http";

import "./App.css";
import "./assets/styles/shared.css";

function App() {
  const { setResumes, setIsFetchingResumes } = useResumesContext();
  const { isFetching, fetchedData } = useFetch(fetchUserResumes); //TODO: Error handling

  // Update the fetching status in the resumes context
  useEffect(() => {
    setIsFetchingResumes(isFetching);
  }, [isFetching, setIsFetchingResumes]);

  // Update the resumes array in the resumes context
  useEffect(() => {
    if (fetchedData) {
      setResumes(fetchedData);
    }
  }, [fetchedData, setResumes]);

  return (
    <div className="App">
        <ResumeTailorForm />
    </div>
  );
}

export default App;

import useFetch from "./hooks/useFetch";
import { fetchJobPostingText } from "./http";

import "./App.css";
import JobPosting from "./components/JobPosting/JobPosting";


function App() {
  const { isFetching, fetchedData: jobPostingText } = useFetch(
    fetchJobPostingText,
    null
  );

  return (
    <div className="App">
      <header className="App-header">
        <JobPosting isFetching={isFetching} jobPostingText={jobPostingText} />
      </header>
    </div>
  );
}

export default App;

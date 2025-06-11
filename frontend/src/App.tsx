import useFetch from "./hooks/useFetch";
import { fetchJobDescriptionText } from "./http";

import "./App.css";
import JobPosting from "./components/JobPosting/JobPosting";


function App() {
  const { isFetching, fetchedData: data, error } = useFetch(fetchJobDescriptionText);

  let jobDescriptionText = null;
  if (data) {
    jobDescriptionText = data['jobDescriptionText'];
  }

  return (
    <div className="App">
      <header className="App-header">
        <JobPosting isFetching={isFetching} jobDescriptionText={jobDescriptionText} error={error} />
      </header>
    </div>
  );
}

export default App;

// import useFetch from "./hooks/useFetch";
// import { fetchJobDescriptionText } from "./http";

import "./App.css";
import "./assets/styles/shared.css";
// import JobPosting from "./components/JobPosting/JobPosting";
import ResumeTailorForm from "./components/ResumeTailorForm/ResumeTailorForm";

function App() {
  // const { isFetching, fetchedData: data, error } = useFetch(fetchJobDescriptionText);

  // let jobDescriptionText = null;
  // if (data) {
  //   jobDescriptionText = data['jobDescriptionText'];
  // }

  return (
    <div className="App">
        {/* <JobPosting isFetching={isFetching} jobDescriptionText={jobDescriptionText} error={error} /> */}
        <ResumeTailorForm />
    </div>
  );
}

export default App;

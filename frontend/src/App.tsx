// import useFetch from "./hooks/useFetch";

import "./App.css";
import "./assets/styles/shared.css";

// import { fetchJobDescriptionText } from "./http";
import { ResumeContextProvider } from "./contexts/ResumeContext";

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
      <ResumeContextProvider>
        <ResumeTailorForm />
      </ResumeContextProvider>
    </div>
  );
}

export default App;

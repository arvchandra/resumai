import type { JobPostingProps } from "../../interfaces/JobPosting"

export default function JobPosting({ isFetching, jobDescriptionText, error } : JobPostingProps) {
  return (
      <>
        {error && <div>{error}</div>}
        {!error && <div>{isFetching ? 'loading...' : jobDescriptionText}</div>}
      </>
  )
}
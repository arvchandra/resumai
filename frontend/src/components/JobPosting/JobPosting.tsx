import type { JobPostingProps } from "../../interfaces/JobPosting"

export default function JobPosting({ isFetching, jobPostingText } : JobPostingProps) {
    return (
        <div>{isFetching ? 'loading...' : jobPostingText}</div>
    )
}
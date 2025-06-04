interface JobPostingProps {
    isFetching: boolean;
    jobPostingText: string;
}

export default function JobPosting({ isFetching, jobPostingText }: JobPostingProps) {
    return (
        <div>{jobPostingText}</div>
    )
}
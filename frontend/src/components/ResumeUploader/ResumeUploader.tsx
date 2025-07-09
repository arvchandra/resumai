import { useCallback, useState } from "react";
import { useDropzone } from "react-dropzone";


enum ResumeType {
  Default = 0
}

interface FilePayload {
  file: File;
  user_id: 2;
  type: ResumeType.Default;
}

type FormDataKeys = keyof FilePayload


export default function ResumeUploader() {
  const handleUpload = async (file: File) => {
    if (file) {
      const formData = new FormData;
      formData.append('file', file);

      try {
        const result = await fetch('http://127.0.0.1:8000/tailor/users/2/resumes/upload', {
          method: 'POST',
          body: formData
        });

        const data = await result.json();

        console.log(data);
      } catch (error) {
        console.error(error);
      }
    }
  }

  const onDrop = useCallback((acceptedFiles: File[]) => {
    handleUpload(acceptedFiles[0]);
    // const file = new FileReader;

    // file.readAsDataURL(acceptedFiles[0]);

    // file.onload = () => {
    //   const base64String = file.result as string;
    //   console.log(base64String);
    // }
  }, []);


  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    accept: {
      'application/pdf': ['.pdf'],
      'application/msword': ['.doc'],
      'application/vnd.openxmlformats-officedocument.wordprocessingml.document': ['.docx'],
    },
    onDrop,
    onDropRejected: (rejectedFiles) => {
      console.log(rejectedFiles);
    }
  });


  return (
    <div {...getRootProps()}>
      <input {...getInputProps()} />
      {
        isDragActive ?
          <p>Drop here ...</p> :
          <p>Drag 'n' drop your resume here</p>
      }

    </div>
  )
}

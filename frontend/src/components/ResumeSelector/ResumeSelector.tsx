export default function ResumeSelector() {
  return (
    <div className="form-field">
      <label htmlFor="resume">Choose a resume:</label>
      <select id="resume" name="resume">
        <option value="resume1">Arvind Chandra_Django Resume_2025</option>
        <option value="resume2">Arvind Chandra_React Resume_2025</option>
      </select>
    </div>
  )
}
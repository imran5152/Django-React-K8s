import { useEffect, useMemo, useState } from "react";
import axios from "axios";
import "./App.css";

const EMPTY_FORM = { name: "", city: "", age: "" };

function initials(name) {
  return name
    .split(/\s+/)
    .filter(Boolean)
    .slice(0, 2)
    .map((part) => part[0].toUpperCase())
    .join("");
}

function App() {
  const [students, setStudents] = useState([]);
  const [status, setStatus] = useState("loading"); // loading | ready | error
  const [query, setQuery] = useState("");
  const [form, setForm] = useState(EMPTY_FORM);
  const [formError, setFormError] = useState("");
  const [actionError, setActionError] = useState("");
  const [saving, setSaving] = useState(false);
  const [attempt, setAttempt] = useState(0);

  useEffect(() => {
    let cancelled = false;
    axios
      .get("/students")
      .then((response) => {
        if (cancelled) return;
        setStudents(response.data);
        setStatus("ready");
      })
      .catch((error) => {
        if (cancelled) return;
        console.error("Error fetching students:", error);
        setStatus("error");
      });
    return () => {
      cancelled = true;
    };
  }, [attempt]);

  const visible = useMemo(() => {
    const term = query.trim().toLowerCase();
    if (!term) return students;
    return students.filter(
      (s) =>
        s.name.toLowerCase().includes(term) || s.city.toLowerCase().includes(term)
    );
  }, [students, query]);

  function retry() {
    setStatus("loading");
    setAttempt((n) => n + 1);
  }

  function updateField(event) {
    setForm((prev) => ({ ...prev, [event.target.name]: event.target.value }));
  }

  async function handleAdd(event) {
    event.preventDefault();
    const name = form.name.trim();
    const city = form.city.trim();
    const age = Number(form.age);

    if (!name || !city || !Number.isInteger(age) || age < 1 || age > 120) {
      setFormError("Enter a name, a city and an age between 1 and 120.");
      return;
    }

    setSaving(true);
    setFormError("");
    try {
      const { data } = await axios.post("/students", { name, age, city });
      setStudents((prev) => [...prev, data]);
      setForm(EMPTY_FORM);
    } catch (error) {
      setFormError(
        error.response?.data?.error ?? "Could not add the student. Try again."
      );
    } finally {
      setSaving(false);
    }
  }

  async function handleRemove(student) {
    setActionError("");
    try {
      await axios.delete(`/students/${student.id}`);
      setStudents((prev) => prev.filter((s) => s.id !== student.id));
    } catch {
      setActionError(`Could not remove ${student.name}. Try again.`);
    }
  }

  return (
    <main className="page">
      <header className="page-header">
        <h1>College students</h1>
        <p>
          {status === "ready"
            ? `${students.length} ${students.length === 1 ? "student" : "students"} enrolled`
            : "Student directory"}
        </p>
      </header>

      <section className="panel" aria-labelledby="add-heading">
        <h2 id="add-heading">Add a student</h2>
        <form className="add-form" onSubmit={handleAdd} noValidate>
          <label className="field">
            Name
            <input name="name" value={form.name} onChange={updateField} autoComplete="off" />
          </label>
          <label className="field">
            City
            <input name="city" value={form.city} onChange={updateField} autoComplete="off" />
          </label>
          <label className="field">
            Age
            <input
              name="age"
              type="number"
              inputMode="numeric"
              min="1"
              max="120"
              value={form.age}
              onChange={updateField}
            />
          </label>
          <button className="btn" type="submit" disabled={saving}>
            {saving ? "Adding..." : "Add student"}
          </button>
        </form>
        {formError && (
          <p className="message" role="alert">
            {formError}
          </p>
        )}
      </section>

      <div className="directory-bar">
        <h2>Directory</h2>
        <label className="search">
          <input
            type="search"
            placeholder="Search by name or city"
            aria-label="Search students by name or city"
            value={query}
            onChange={(e) => setQuery(e.target.value)}
          />
        </label>
      </div>

      {actionError && (
        <p className="message" role="alert">
          {actionError}
        </p>
      )}

      <div className="table-wrap">
        {status === "loading" && <p className="state">Loading students...</p>}

        {status === "error" && (
          <div className="state" role="alert">
            <p>Can't reach the students API. Check that the backend is running, then try again.</p>
            <button className="btn" onClick={retry}>
              Try again
            </button>
          </div>
        )}

        {status === "ready" && students.length === 0 && (
          <p className="state">No students yet. Add the first one above.</p>
        )}

        {status === "ready" && students.length > 0 && visible.length === 0 && (
          <p className="state">No student matches "{query}".</p>
        )}

        {status === "ready" && visible.length > 0 && (
          <table>
            <thead>
              <tr>
                <th>Name</th>
                <th>City</th>
                <th className="num">Age</th>
                <th aria-label="Actions"></th>
              </tr>
            </thead>
            <tbody>
              {visible.map((student) => (
                <tr key={student.id}>
                  <td>
                    <div className="student">
                      <span className="avatar" aria-hidden="true">
                        {initials(student.name)}
                      </span>
                      {student.name}
                    </div>
                  </td>
                  <td>{student.city}</td>
                  <td className="num">{student.age}</td>
                  <td className="actions">
                    <button
                      className="btn-quiet"
                      onClick={() => handleRemove(student)}
                      aria-label={`Remove ${student.name}`}
                    >
                      Remove
                    </button>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        )}
      </div>
    </main>
  );
}

export default App;

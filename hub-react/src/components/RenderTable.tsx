// RenderTable.tsx
import React from "react";
import { RenderTableProps } from "../interfaces/interfaces";
import parse from "html-react-parser";
import ScrapeAgainButton from "./ScrapeAgainButton";
import useExpandedRows from "../hooks/useExpandRows";
import "../styles/RenderTable.css"; // Ensure this CSS file contains the styles mentioned above
import ToggleStatusButton from "./ToggleStatusButton";

const RenderTable: React.FC<RenderTableProps> = ({
  emails,
  rootData,
  onScrapeAgain,
  onStatusUpdate,
}) => {
  const { expandedRows, toggleDiff } = useExpandedRows();

  return (
    <div>
      <table>
        <thead>
          <tr>
            <th>Email</th>
          </tr>
        </thead>
        <tbody>
          {emails.map((email, index) => (
            <tr key={index}>
              <td>{email}</td>
            </tr>
          ))}
        </tbody>
      </table>
      <hr></hr>

      <div>
        {/* <h2>Root Data</h2>
        <p>Keywords: {rootData.keywords}</p>
        <p>Schedules: {rootData.schedules}</p> */}
        <h3>Grants:</h3>
        <table id="grant-table">
          <colgroup>
            <col style={{ width: "25%" }} />
            <col style={{ width: "25%" }} />
            <col style={{ width: "25%" }} />
            <col style={{ width: "25%" }} />
          </colgroup>
          <thead>
            <tr>
              <th>Grant Program Page</th>
              <th>Last Scrape DateTime</th> {/* Remove inline sort for now */}
              <th>Change Status</th>
              <th>Actions</th>
            </tr>
          </thead>
          <tbody>
            {rootData.grants.map((grant) => (
              <React.Fragment key={grant.page}>
                <tr
                  id={grant.page}
                  className={
                    grant.status.includes("SIGNIFICANT CHANGE!")
                      ? "significant"
                      : grant.status.includes("TRIVIAL CHANGE!")
                      ? "trivial"
                      : "default"
                  }
                >
                  <td>{grant.page}</td>
                  <td>{grant.date}</td>
                  <td>
                    {grant.status}
                    <span className="review-timestamp"></span>
                  </td>
                  <td>
                    <button onClick={() => toggleDiff(grant.page)}>
                      View Details
                    </button>
                    <ScrapeAgainButton grant={grant} onScrape={onScrapeAgain} />
                    {/* <button class="show-prior-diff-btn" data-url="{{ grant.page }}"
                    {% if grant.status == 'Invalid' %}disabled{% endif %} >Show Previous Change</button> */}
                    <ToggleStatusButton
                      grant={grant}
                      onToggle={onStatusUpdate}
                    />
                    {/*                    
                    <button id="email-button" onclick="promptEmail(this)">Email This</button>
                    <button onclick="markAsReviewed(this, '{{grant.date}}')"
                    {% if grant.status == 'Invalid' %}disabled{% endif %}>Mark as Reviewed</button>
                    <button onclick="deleteRow(this)">Delete Row</button> */}
                  </td>
                </tr>
                {expandedRows[grant.page] && (
                  <tr className="diff-row">
                    <td colSpan={4}>{parse(grant.diff)}</td>
                  </tr>
                )}
              </React.Fragment>
            ))}
          </tbody>
        </table>
      </div>
    </div>
  );
};

export default RenderTable;

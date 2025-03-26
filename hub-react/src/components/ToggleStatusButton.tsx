// ToggleStatusButton.tsx
import React from "react";
import { Grant } from "../interfaces/interfaces";
import { useToggleStatus } from "../hooks/useToggleStatus";

interface ToggleStatusButtonProps {
  grant: Grant;
  onToggle: (updatedGrant: Grant) => void;
}

const ToggleStatusButton: React.FC<ToggleStatusButtonProps> = ({
  grant,
  onToggle,
}) => {
  const { toggleStatus } = useToggleStatus();

  const handleToggle = async () => {
    await toggleStatus(grant, onToggle);
  };

  return (
    <button
      onClick={handleToggle}
      disabled={
        !grant.status.includes("TRIVIAL") &&
        !grant.status.includes("SIGNIFICANT")
      }
    >
      {grant.status.includes("TRIVIAL CHANGE!")
        ? "Flag as SIGNIFICANT CHANGE!"
        : "Flag as TRIVIAL CHANGE!"}
    </button>
  );
};

export default ToggleStatusButton;

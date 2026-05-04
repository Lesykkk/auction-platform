import { getApiError } from "../api/http";

type Props = {
  error: unknown;
};

export const ErrorAlert = ({ error }: Props) => {
  const apiError = getApiError(error);
  const hasDetails = apiError.details.length > 0;

  return (
    <div className="form-error error-alert" role="alert">
      <strong>{apiError.message}</strong>
      {hasDetails && (
        <ul>
          {apiError.details.map((detail) => (
            <li key={detail}>{detail}</li>
          ))}
        </ul>
      )}
      {apiError.status ? <small>HTTP {apiError.status}</small> : null}
    </div>
  );
};

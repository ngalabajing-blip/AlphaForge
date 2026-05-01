export const Spinner = ({ size = 16 }: { size?: number }) => (
  <span
    role="status"
    aria-label="Loading"
    className="inline-block border-2 border-current border-r-transparent rounded-full animate-spin"
    style={{ width: size, height: size }}
  />
);

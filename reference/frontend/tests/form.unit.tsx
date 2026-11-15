import {
  cleanup,
  fireEvent,
  render,
  screen,
  waitFor,
} from "@testing-library/react";
import { afterEach, describe, expect, it, vi } from "vitest";
import { CustomerForm } from "../src/App";
import { saveFailure } from "../src/api";

afterEach(() => {
  cleanup();
  vi.unstubAllGlobals();
  vi.restoreAllMocks();
  sessionStorage.clear();
});

describe("create outcomes", () => {
  it.each([null, 503, 500])(
    "prevents retries after an uncertain outcome (%s)",
    (status) => {
      expect(saveFailure(status).kind).toBe("unconfirmed");
    },
  );

  it.each([400, 409, 413])(
    "allows correction after a known rejection (%s)",
    (status) => {
      expect(saveFailure(status).kind).toBe("error");
    },
  );

  it("renders labels and retains safe input when correction is possible", async () => {
    const request = vi
      .fn()
      .mockResolvedValueOnce(Response.json({ tenant_id: "fixture" }))
      .mockResolvedValueOnce(new Response(null, { status: 409 }));
    vi.stubGlobal("fetch", request);
    const created = vi.fn();
    render(<CustomerForm navigate={vi.fn()} onCreated={created} />);
    const name = screen.getByRole<HTMLInputElement>("textbox", {
      name: "Name",
    });
    const email = screen.getByRole<HTMLInputElement>("textbox", {
      name: "Email",
    });
    fireEvent.change(name, { target: { value: "Ada" } });
    fireEvent.change(email, { target: { value: "ada@example.test" } });
    fireEvent.click(screen.getByRole("button", { name: "Save customer" }));
    const alert = await screen.findByRole("alert");
    expect(alert.textContent).toContain("already exists");
    await waitFor(() => expect(document.activeElement).toBe(alert));
    expect(email.value).toBe("ada@example.test");
    expect(created).not.toHaveBeenCalled();
  });

  it("offers recovery and removes saving after a missing response", async () => {
    const request = vi
      .fn()
      .mockResolvedValueOnce(Response.json({ tenant_id: "fixture" }))
      .mockRejectedValueOnce(new TypeError("Connection lost"));
    vi.stubGlobal("fetch", request);
    const navigate = vi.fn();
    render(<CustomerForm navigate={navigate} onCreated={vi.fn()} />);
    fireEvent.change(screen.getByLabelText("Name"), {
      target: { value: "Ada" },
    });
    fireEvent.change(screen.getByLabelText("Email"), {
      target: { value: "ada@example.test" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Save customer" }));
    expect((await screen.findByRole("alert")).textContent).toContain(
      "could not confirm",
    );
    expect(screen.queryByRole("button", { name: "Save customer" })).toBeNull();
    fireEvent.click(screen.getByRole("link", { name: "Back to customers" }));
    expect(navigate).toHaveBeenCalledWith("/customers");
    expect(request).toHaveBeenCalledTimes(2);
  });

  it("fences a write after leaving and remounting its route", async () => {
    const request = vi
      .fn()
      .mockResolvedValueOnce(Response.json({ tenant_id: "fixture" }))
      .mockImplementationOnce(() => new Promise<Response>(() => {}));
    vi.stubGlobal("fetch", request);
    const form = render(
      <CustomerForm navigate={vi.fn()} onCreated={vi.fn()} />,
    );
    fireEvent.change(screen.getByLabelText("Name"), {
      target: { value: "Ada" },
    });
    fireEvent.change(screen.getByLabelText("Email"), {
      target: { value: "ada@example.test" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Save customer" }));
    await waitFor(() => expect(request).toHaveBeenCalledTimes(2));
    form.unmount();

    render(<CustomerForm navigate={vi.fn()} onCreated={vi.fn()} />);
    expect(screen.getByRole("alert").textContent).toContain(
      "could not confirm",
    );
    expect(screen.queryByRole("button", { name: "Save customer" })).toBeNull();
    expect(request).toHaveBeenCalledTimes(2);
  });

  it("blocks the write when recovery state cannot be recorded", async () => {
    vi.spyOn(Storage.prototype, "setItem").mockImplementation(() => {
      throw new DOMException("Storage unavailable");
    });
    const request = vi
      .fn()
      .mockResolvedValue(Response.json({ tenant_id: "fixture" }));
    vi.stubGlobal("fetch", request);
    render(<CustomerForm navigate={vi.fn()} onCreated={vi.fn()} />);
    fireEvent.change(screen.getByLabelText("Name"), {
      target: { value: "Ada" },
    });
    fireEvent.change(screen.getByLabelText("Email"), {
      target: { value: "ada@example.test" },
    });
    fireEvent.click(screen.getByRole("button", { name: "Save customer" }));
    expect((await screen.findByRole("alert")).textContent).toContain(
      "preserve save recovery",
    );
    expect(request).toHaveBeenCalledTimes(1);
    expect(request).toHaveBeenCalledWith("/session", expect.anything());
  });
});

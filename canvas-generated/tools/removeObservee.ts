
import { tool } from "ai";
import { removeObserveeDataSchema } from "./aitm.schema.ts";
import { removeObservee, RemoveObserveeData } from "..";

export default tool({
  description: `
  Remove an observee
Unregisters a user as being observed by the given user.
    `,
  parameters: removeObserveeDataSchema.omit({ url: true }),
  execute: async (args : Omit<RemoveObserveeData, "url"> ) => {
    try {
      const { data } = await removeObservee(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
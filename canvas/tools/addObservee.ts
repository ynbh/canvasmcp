
import { tool } from "ai";
import { addObserveeDataSchema } from "./aitm.schema.ts";
import { addObservee, AddObserveeData } from "..";

export default tool({
  description: `
  Add an observee
Registers a user as being observed by the given user.
    `,
  parameters: addObserveeDataSchema.omit({ url: true }),
  execute: async (args : Omit<AddObserveeData, "url"> ) => {
    try {
      const { data } = await addObservee(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
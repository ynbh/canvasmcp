
import { tool } from "ai";
import { showObserveeDataSchema } from "./aitm.schema.ts";
import { showObservee, ShowObserveeData } from "..";

export default tool({
  description: `
  Show an observee
Gets information about an observed user.

*Note:* all users are allowed to view
their own observees.
    `,
  parameters: showObserveeDataSchema.omit({ url: true }),
  execute: async (args : Omit<ShowObserveeData, "url"> ) => {
    try {
      const { data } = await showObservee(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
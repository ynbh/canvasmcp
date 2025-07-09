
import { tool } from "ai";
import { redirectToRootOutcomeGroupForContextGlobalDataSchema } from "./aitm.schema.ts";
import { redirectToRootOutcomeGroupForContextGlobal, RedirectToRootOutcomeGroupForContextGlobalData } from "..";

export default tool({
  description: `
  Redirect to root outcome group for context
Convenience redirect to find the root outcome group for a
particular
context. Will redirect to the appropriate outcome group's URL.
    `,
  parameters: redirectToRootOutcomeGroupForContextGlobalDataSchema.omit({ url: true }),
  execute: async (args : Omit<RedirectToRootOutcomeGroupForContextGlobalData, "url"> ) => {
    try {
      const { data } = await redirectToRootOutcomeGroupForContextGlobal(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    

import { tool } from "ai";
import { abortAllPendingSisImportsDataSchema } from "./aitm.schema.ts";
import { abortAllPendingSisImports, AbortAllPendingSisImportsData } from "..";

export default tool({
  description: `
  Abort all pending SIS imports
Abort already created but not processed or processing SIS imports.
    `,
  parameters: abortAllPendingSisImportsDataSchema.omit({ url: true }),
  execute: async (args : Omit<AbortAllPendingSisImportsData, "url"> ) => {
    try {
      const { data } = await abortAllPendingSisImports(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
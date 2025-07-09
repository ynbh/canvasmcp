
import { tool } from "ai";
import { abortSisImportDataSchema } from "./aitm.schema.ts";
import { abortSisImport, AbortSisImportData } from "..";

export default tool({
  description: `
  Abort SIS import
Abort a SIS import that has not completed.
    `,
  parameters: abortSisImportDataSchema.omit({ url: true }),
  execute: async (args : Omit<AbortSisImportData, "url"> ) => {
    try {
      const { data } = await abortSisImport(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
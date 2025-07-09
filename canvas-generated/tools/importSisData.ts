
import { tool } from "ai";
import { importSisDataDataSchema } from "./aitm.schema.ts";
import { importSisData, ImportSisDataData } from "..";

export default tool({
  description: `
  Import SIS data
Import SIS data into Canvas. Must be on a root account with SIS
imports
enabled.

For more information on the format that's expected here, please see the
"SIS CSV"
section in the API docs.
    `,
  parameters: importSisDataDataSchema.omit({ url: true }),
  execute: async (args : Omit<ImportSisDataData, "url"> ) => {
    try {
      const { data } = await importSisData(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
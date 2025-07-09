
import { tool } from "ai";
import { showEpubExportDataSchema } from "./aitm.schema.ts";
import { showEpubExport, ShowEpubExportData } from "..";

export default tool({
  description: `
  Show ePub export
Get information about a single ePub export.
    `,
  parameters: showEpubExportDataSchema.omit({ url: true }),
  execute: async (args : Omit<ShowEpubExportData, "url"> ) => {
    try {
      const { data } = await showEpubExport(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
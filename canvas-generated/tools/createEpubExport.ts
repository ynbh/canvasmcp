
import { tool } from "ai";
import { createEpubExportDataSchema } from "./aitm.schema.ts";
import { createEpubExport, CreateEpubExportData } from "..";

export default tool({
  description: `
  Create ePub Export
Begin an ePub export for a course.

You can use the {api:ProgressController#show
Progress API} to track the
progress of the export. The export's progress is linked to with
the
_progress_url_ value.

When the export completes, use the {api:EpubExportsController#show Show
content export} endpoint
to retrieve a download URL for the exported content.
    `,
  parameters: createEpubExportDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateEpubExportData, "url"> ) => {
    try {
      const { data } = await createEpubExport(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
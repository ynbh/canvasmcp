
import { tool } from "ai";
import { exportContentGroupsDataSchema } from "./aitm.schema.ts";
import { exportContentGroups, ExportContentGroupsData } from "..";

export default tool({
  description: `
  Export content
Begin a content export job for a course, group, or user.

You can use the
{api:ProgressController#show Progress API} to track the
progress of the export. The migration's
progress is linked to with the
_progress_url_ value.

When the export completes, use the
{api:ContentExportsApiController#show Show content export} endpoint
to retrieve a download URL for
the exported content.
    `,
  parameters: exportContentGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<ExportContentGroupsData, "url"> ) => {
    try {
      const { data } = await exportContentGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
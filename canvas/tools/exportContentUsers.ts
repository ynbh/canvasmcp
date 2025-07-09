
import { tool } from "ai";
import { exportContentUsersDataSchema } from "./aitm.schema.ts";
import { exportContentUsers, ExportContentUsersData } from "..";

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
  parameters: exportContentUsersDataSchema.omit({ url: true }),
  execute: async (args : Omit<ExportContentUsersData, "url"> ) => {
    try {
      const { data } = await exportContentUsers(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
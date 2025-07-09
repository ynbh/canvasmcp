
import { tool } from "ai";
import { createContentMigrationGroupsDataSchema } from "./aitm.schema.ts";
import { createContentMigrationGroups, CreateContentMigrationGroupsData } from "..";

export default tool({
  description: `
  Create a content migration
Create a content migration. If the migration requires a file to be
uploaded
the actual processing of the file will start once the file upload process is
completed.
File uploading works as described in the {file:file_uploads.html File Upload
Documentation}
except that the values are set on a *pre_attachment* sub-hash.

For migrations that
don't require a file to be uploaded, like course copy, the
processing will begin as soon as the
migration is created.

You can use the {api:ProgressController#show Progress API} to track
the
progress of the migration. The migration's progress is linked to with the
_progress_url_
value.

The two general workflows are:

If no file upload is needed:

1. POST to create
2. Use the
{api:ProgressController#show Progress} specified in _progress_url_ to monitor progress

For file
uploading:

1. POST to create with file info in *pre_attachment*
2. Do {file:file_uploads.html file
upload processing} using the data in the *pre_attachment* data
3.
{api:ContentMigrationsController#show GET} the ContentMigration
4. Use the
{api:ProgressController#show Progress} specified in _progress_url_ to monitor progress

(required if
doing .zip file upload)
    `,
  parameters: createContentMigrationGroupsDataSchema.omit({ url: true }),
  execute: async (args : Omit<CreateContentMigrationGroupsData, "url"> ) => {
    try {
      const { data } = await createContentMigrationGroups(args);
      return data;
    } catch (e: unknown) {
      console.log(e);
      return "no results";
    }
  },
});
    
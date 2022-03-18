from . import controllers
from . import fields
from . import models
from . import wizards
from . import jobrunner

# shortcuts
from .job import identity_exact

import logging

logger = logging.getLogger(__name__)


def post_init_hook(cr, registry):
    # this is the trigger that sends notifications when jobs change
    logger.info("Create queue_job_notify trigger")
    cr.execute(
        """
            DROP TRIGGER IF EXISTS queue_job_notify ON queue_job;
            CREATE OR REPLACE
                FUNCTION queue_job_notify() RETURNS trigger AS $$
            BEGIN
                IF TG_OP = 'DELETE' THEN
                    IF OLD.state != 'done' THEN
                        PERFORM pg_notify('queue_job', OLD.uuid);
                    END IF;
                ELSE
                    PERFORM pg_notify('queue_job', NEW.uuid);
                END IF;
                RETURN NULL;
            END;
            $$ LANGUAGE plpgsql;
            CREATE TRIGGER queue_job_notify
                AFTER INSERT OR UPDATE OR DELETE
                ON queue_job
                FOR EACH ROW EXECUTE PROCEDURE queue_job_notify();
        """
    )

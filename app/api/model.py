# Local application imports
from app.extensions import db


class Model(db.Model):
    __abstract__ = True

    def __init__(self, *arg, **kwargs):
        super().__init__(*arg, **kwargs)


class CRUDModelMixin:
    __table_args__ = {"extend_existing": True}
    # https://docs.sqlalchemy.org/en/13/core/metadata.html?highlight=\
    # extend_existing#sqlalchemy.schema.Table.params.extend_existing

    session = None

    def __init__(self, session=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.session = session or db.session

    @classmethod
    def find(cls, **kwargs):
        return cls.query.filter_by(**kwargs).first()

    @classmethod
    def find_or_create(cls, commit=True, **kwargs):
        obj = cls.find(**kwargs)
        if not obj:
            obj = cls.create(commit=commit, **kwargs)
        return obj

    @classmethod
    def get_by_id(cls, id):
        if any((isinstance(id, str) and id.isdigit(), isinstance(id, (int, float))),):
            return cls.query.get(int(id))
        raise TypeError("Invalid id")

    @classmethod
    def filter(cls, filters):
        """
        Return filtered queryset based on filter.
        :param filters: A list of filters, ie: [(key,operator,value)]
        operator list:
            eq for ==
            lt for <
            ge for >=
            in for in_
            like for like
            value could be list or a string
        :return: queryset
        """
        if not isinstance(filters, list):
            raise TypeError("Invalid filters")

        if not all([isinstance(f, tuple) for f in filters]):
            raise TypeError("Invalid filters")

        query = cls.query

        for f in filters:
            # Unpack the filter
            try:
                key, op, value = f
            except ValueError:
                raise ValueError(f"Invalid filter: {str(f)}")

            # Get the column to be filtered
            column = getattr(cls, key, None)

            if column is None:
                raise ValueError("Invalid filter column: %s" % key)

            # Filter by value using operator
            if op == "in":
                if isinstance(value, list):
                    query_filter = column.in_(value)
                else:
                    query_filter = column.in_(value.split(","))
            else:
                try:
                    attr = (
                        list(
                            filter(
                                lambda e: hasattr(column, e % op),
                                ["%s", "%s_", "__%s__"],
                            )
                        )[0]
                        % op
                    )
                except IndexError:
                    raise ValueError("Invalid filter operator: %s" % op)

                if value == "null":
                    value = None

                query_filter = getattr(column, attr)(value)

            # Apply the filter
            query = query.filter(query_filter)
        return query

    @classmethod
    def create(cls, commit=True, **kwargs):
        instance = cls(**kwargs)
        obj = instance.save(commit)
        return obj

    def update(self, commit=True, **kwargs):
        for attr, value in kwargs.items():
            assert hasattr(self, attr)
            setattr(self, attr, value)
        return commit and self.save() or self

    def save(self, commit=True):
        self.session.add(self)
        if commit is True:
            self.session.commit()
        return self

    def delete(self, commit=True):
        self.session.delete(self)
        if commit is True:
            self.session.commit()
        return
